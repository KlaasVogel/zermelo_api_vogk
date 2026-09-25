"""Tests for deriving stamklassen from language lessons. Synthetic data only."""

import asyncio
from datetime import datetime

import pytest

from zermelo_api.src import stamklassen as sk
from zermelo_api.src.groepen import Groep, Groepen
from zermelo_api.src.stamklassen import StamklasLes, group_to_stamklas, resolve_stamklassen

DEPT_1A, DEPT_1G, DEPT_4H, DEPT_5V, DEPT_6V = 11, 12, 40, 51, 61  # departmentOfBranch ids


def groep(id: int, name: str, department: int, main: bool = True) -> Groep:
    return Groep(id, main, main, department, name, name)


MAIN_GROUPS = [
    groep(1, "lg1a1", DEPT_1A),
    groep(2, "lg1g1", DEPT_1G),
    groep(3, "lg4h1", DEPT_4H),
    groep(4, "lg4h2", DEPT_4H),
    groep(5, "lg5v2", DEPT_5V),
    groep(6, "lg6v1", DEPT_6V),
]
MAIN_NAMES = {g.name for g in MAIN_GROUPS}


def les(subject: str, groups: list[str], students: list[int], valid: bool = True) -> StamklasLes:
    return StamklasLes([subject], groups, [str(s) for s in students], valid)


@pytest.mark.parametrize(
    "group, expected",
    [
        ("lg4h.netl2", "lg4h2"),
        ("lg1a.ne1", "lg1a1"),
        ("lg1a1", "lg1a1"),  # a main group name itself
        ("lg4h.netl9", None),  # no such stamklas
        ("lg4h.nlt1", "lg4h1"),  # parses, but subject filtering happens elsewhere
        ("wiskunde", None),
    ],
)
def test_group_to_stamklas(group, expected):
    assert group_to_stamklas(group, MAIN_NAMES) == expected


def test_single_group_lesson():
    result = resolve_stamklassen([les("netl", ["lg4h.netl2"], [1001, 1002])], MAIN_GROUPS)
    assert result == {1001: "lg4h2", 1002: "lg4h2"}


def test_single_group_beats_combined_lesson():
    lessons = [
        les("ne", ["lg1a.ne1"], [1001]),
        les("ne", ["lg1a.ne1", "lg1g.ne1"], [1001, 2001]),
    ]
    result = resolve_stamklassen(lessons, MAIN_GROUPS)
    assert result[1001] == "lg1a1"


def test_combined_lesson_alone_is_ambiguous():
    result = resolve_stamklassen([les("ne", ["lg1a.ne1", "lg1g.ne1"], [2001])], MAIN_GROUPS)
    assert 2001 not in result


def test_combined_lesson_resolved_by_single_class_lesson_in_other_subject():
    # G pupils share Nederlands with A, but only G has Greek ("gr") as its own class
    lessons = [
        les("ne", ["lg1a.ne1", "lg1g.ne1"], [2001, 2002]),
        les("gr", ["lg1g.gr1"], [2001]),
        les("du", ["lg1a.du1"], [2002]),
    ]
    assert resolve_stamklassen(lessons, MAIN_GROUPS) == {2001: "lg1g1", 2002: "lg1a1"}


def test_single_class_lesson_outside_candidates_does_not_count():
    lessons = [
        les("ne", ["lg1a.ne1", "lg1g.ne1"], [2001]),
        les("wisb", ["lg4h.wisb1"], [2001]),
    ]
    assert resolve_stamklassen(lessons, MAIN_GROUPS) == {}


def test_first_subject_wins_over_fallback():
    # a 5V pupil taking English in 6V: netl (own year) must win over entl
    lessons = [
        les("netl", ["lg5v.netl2"], [3001]),
        les("entl", ["lg6v.entl1"], [3001]),
    ]
    assert resolve_stamklassen(lessons, MAIN_GROUPS) == {3001: "lg5v2"}


def test_fallback_subject_when_first_is_missing():
    assert resolve_stamklassen([les("entl", ["lg4h.entl1"], [3002])], MAIN_GROUPS) == {3002: "lg4h1"}


def test_conflicting_single_groups_are_ambiguous():
    lessons = [les("netl", ["lg4h.netl1"], [4001]), les("netl", ["lg4h.netl2"], [4001])]
    assert resolve_stamklassen(lessons, MAIN_GROUPS) == {}


def test_ignores_invalid_lessons_and_other_subjects():
    lessons = [
        les("netl", ["lg4h.netl1"], [5001], valid=False),
        les("nlt", ["lg4h.nlt1"], [5002]),
    ]
    assert resolve_stamklassen(lessons, MAIN_GROUPS) == {}


def make_groepen() -> Groepen:
    groepen = Groepen()
    groepen.extend(MAIN_GROUPS)
    groepen.append(groep(99, "lg4h.netl1", DEPT_4H, main=False))
    return groepen


def test_find_stamklassen_queries_main_groups_only(monkeypatch):
    queries: list[str] = []

    async def fake_load_query(query: str) -> list[dict]:
        queries.append(query)
        if "GroupInDepartment=3&" in query:
            return [{"subjects": ["netl"], "groups": ["lg4h.netl1"], "students": ["1001"], "valid": True}]
        return []

    monkeypatch.setattr(sk.zermelo, "load_query", fake_load_query)
    result = asyncio.run(sk.find_stamklassen(make_groepen(), datetime(2026, 9, 21)))
    assert result == {1001: "lg4h1"}
    assert len(queries) == len(MAIN_GROUPS)
    assert not any("subjects=" in q for q in queries)  # all subjects: needed for the A/G tiebreak


def test_find_stamklassen_tries_next_window_when_empty(monkeypatch):
    starts: list[int] = []

    async def fake_load_query(query: str) -> list[dict]:
        start = int(query.split("&start=")[1].split("&")[0])
        if start not in starts:
            starts.append(start)
        if len(starts) < 2:
            return []  # first window: holiday
        return [{"subjects": ["ne"], "groups": ["lg1a.ne1"], "students": ["1001"], "valid": True}]

    monkeypatch.setattr(sk.zermelo, "load_query", fake_load_query)
    result = asyncio.run(sk.find_stamklassen(make_groepen(), datetime(2026, 9, 21), weeks=2))
    assert result == {1001: "lg1a1"}
    assert starts[1] - starts[0] == 14 * 24 * 3600


def test_find_stamklassen_gives_up_after_max_tries(monkeypatch):
    calls = 0

    async def fake_load_query(query: str) -> list[dict]:
        nonlocal calls
        calls += 1
        return []

    monkeypatch.setattr(sk.zermelo, "load_query", fake_load_query)
    assert asyncio.run(sk.find_stamklassen(make_groepen(), datetime(2026, 9, 21), max_tries=2)) == {}
    assert calls == 2 * len(MAIN_GROUPS)
