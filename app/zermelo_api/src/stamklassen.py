"""Derive each pupil's stamklas (main group) from their lessons.

The direct routes (users.mainGroup, studentsindepartments, groupindepartments.students)
need read rights an ordinary API token usually doesn't have. The main groups themselves
*are* readable, and so are lessons per main group
(appointments?containsStudentsFromGroupInDepartment=...). Language lessons are taught
per stamklas: e.g. group "lg4h.netl2" is stamklas "lg4h2". So a pupil's stamklas is
derived from the group names of their Nederlands lessons, with English as fallback.

Subjects are tried in order; the first one giving exactly one stamklas wins. The
default ("ne", "netl", "entl") covers Nederlands in the lower ("ne") and upper
("netl") years, falling back to English ("entl") for pupils without a Nederlands group.

Classes that share their language lessons (e.g. "lg3a.ne1" + "lg3g.ne1" in one lesson)
are told apart by any single-class lesson the pupil has in another subject (e.g. Greek
"lg3g.gr1" -> "lg3g1"). The pupil's department isn't used: it's derived from lesgroepen,
and combined A/G subjects are registered under one department, so it's unreliable exactly
where it would be needed.
"""

from __future__ import annotations
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import asyncio
import re
import logging

from ._zermelo_api import zermelo
from .groepen import Groep, Groepen

logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)

STAMKLAS_SUBJECTS: tuple[str, ...] = ("ne", "netl", "entl")

# "lg4h.netl2" -> department "lg4h", number "2"
GROUP_PART = re.compile(r"^(?P<dept>[a-z]+\d+[a-z]+)\.[a-z]+?(?P<nr>\d+)$")


@dataclass
class StamklasLes:
    """The parts of an appointment needed to derive stamklassen."""

    subjects: list[str]
    groups: list[str]
    students: list[str]
    valid: bool = True

    @classmethod
    def from_dict(cls, data: dict) -> StamklasLes:
        return cls(
            subjects=data.get("subjects") or [],
            groups=data.get("groups") or [],
            students=data.get("students") or [],
            valid=data.get("valid", True),
        )


def group_to_stamklas(group_name: str, main_names: set[str]) -> str | None:
    """Maps one lesson group name to the stamklas it stands for.

    Args:
        group_name: A lesson group, e.g. "lg4h.netl2", or a main group name itself (e.g. "lg1ha1").
        main_names: Names of all main groups (stamklassen) of the branch.

    Returns:
        The stamklas name (e.g. "lg4h2"), or None if the group doesn't map to an existing stamklas.
    """
    if group_name in main_names:
        return group_name
    match = GROUP_PART.match(group_name)
    if not match:
        return None
    name = match["dept"] + match["nr"]
    return name if name in main_names else None


@dataclass
class _Candidates:
    """Stamklas candidates for one pupil and one subject."""

    strong: set[str] = field(default_factory=set)  # from lessons with a single group
    weak: set[str] = field(default_factory=set)  # from combined lessons (several groups)


def resolve_stamklassen(
    lessons: Sequence[StamklasLes],
    main_groups: Sequence[Groep],
    subjects: Sequence[str] = STAMKLAS_SUBJECTS,
) -> dict[int, str]:
    """Derives a stamklas per pupil from their lessons (pure function, no API calls).

    For each pupil, subjects are tried in order:
    1. a lesson of that subject with a single group decides ("lg4h.netl2" -> "lg4h2");
    2. with only combined lessons of that subject (e.g. "lg3a.ne1" + "lg3g.ne1"), the
       candidate the pupil also has a single-class lesson for, in any subject, decides.
    Pupils that stay ambiguous are left out.

    Args:
        lessons: Lessons (appointments), all subjects: other subjects are needed for step 2.
        main_groups: All main groups (stamklassen) of the branch.
        subjects: Subject codes in order of preference.

    Returns:
        leerlingnummer -> stamklas name, only for pupils with an unambiguous stamklas.
    """
    main_names = {groep.name for groep in main_groups}
    per_pupil: dict[int, dict[str, _Candidates]] = {}
    single_class: dict[int, set[str]] = {}  # every stamklas a pupil has a single-group lesson for
    for les in lessons:
        if not les.valid:
            continue
        stamklassen = {name for name in (group_to_stamklas(g, main_names) for g in les.groups) if name}
        if not stamklassen:
            continue
        single = len(les.groups) == 1
        for student in les.students:
            llnr = int(student)
            if single:
                single_class.setdefault(llnr, set()).update(stamklassen)
            for subject in les.subjects:
                if subject not in subjects:
                    continue
                candidates = per_pupil.setdefault(llnr, {}).setdefault(subject, _Candidates())
                (candidates.strong if single else candidates.weak).update(stamklassen)

    result: dict[int, str] = {}
    for llnr, by_subject in per_pupil.items():
        for subject in subjects:
            candidates = by_subject.get(subject)
            if not candidates:
                continue
            stamklas = _pick(candidates, single_class.get(llnr, set()))
            if stamklas:
                result[llnr] = stamklas
                break
    return result


def _pick(candidates: _Candidates, single_class: set[str]) -> str | None:
    if candidates.strong:
        return next(iter(candidates.strong)) if len(candidates.strong) == 1 else None
    confirmed = candidates.weak & single_class
    return next(iter(confirmed)) if len(confirmed) == 1 else None


async def load_stamklas_lessons(main_groups: Sequence[Groep], start: int, end: int) -> list[StamklasLes]:
    """Loads all lessons of every main group's pupils, one query per main group."""
    fields = "students,groups,subjects,valid"
    queries = [
        f"appointments/?containsStudentsFromGroupInDepartment={groep.id}"
        f"&type=lesson&start={start}&end={end}&fields={fields}"
        for groep in main_groups
    ]
    results = await asyncio.gather(*[zermelo.load_query(query) for query in queries])
    return [StamklasLes.from_dict(row) for rows in results for row in rows]


async def find_stamklassen(
    groepen: Groepen,
    date: datetime | None = None,
    weeks: int = 2,
    subjects: Sequence[str] = STAMKLAS_SUBJECTS,
    max_tries: int = 3,
) -> dict[int, str]:
    """Finds each pupil's stamklas from their language lessons.

    Looks at a window of `weeks` weeks from `date`. If that window has no lessons at all
    (e.g. a holiday), the next window is tried, up to `max_tries` windows.

    Args:
        groepen: All groups of the branch (Branch.groepen); only main groups are used.
        date: Start of the lesson window (default: now).
        weeks: Length of the lesson window in weeks.
        subjects: Subject codes in order of preference.
        max_tries: Maximum number of consecutive windows to try.

    Returns:
        leerlingnummer -> stamklas name (e.g. "lg4h2"); pupils without an unambiguous stamklas are left out.
    """
    main_groups = [groep for groep in groepen if groep.isMainGroup]
    if not main_groups:
        logger.warning("no main groups found, cannot derive stamklassen")
        return {}
    start = date or datetime.now()
    for attempt in range(max_tries):
        window_start = start + timedelta(weeks=attempt * weeks)
        window_end = window_start + timedelta(weeks=weeks)
        lessons = await load_stamklas_lessons(main_groups, int(window_start.timestamp()), int(window_end.timestamp()))
        if lessons:
            result = resolve_stamklassen(lessons, main_groups, subjects)
            logger.info(
                f"stamklassen: {len(result)} pupils linked, from {len(lessons)} lessons "
                f"({window_start:%Y-%m-%d} - {window_end:%Y-%m-%d})"
            )
            return result
        logger.debug(f"no lessons from {window_start:%Y-%m-%d}, trying next window")
    logger.warning(f"no lessons found in {max_tries} windows of {weeks} weeks, no stamklassen derived")
    return {}
