from dataclasses import dataclass, field, InitVar
from .vakken import Vakken, Vak
from .groepen import Groepen, Groep
from .users import Leerlingen, Leerling, Personeel, Medewerker
from .leerjaren import Leerjaren, Leerjaar
from .time_utils import get_date, delta_week
from .zermelo_api import from_zermelo_dict
import logging

logger = logging.getLogger(__name__)


def createLesgroepNaam(vak: Vak, groep: Groep) -> str:
    leerjaar, groepnaam = groep.extendedName.split(".")
    jaarnaam = leerjaar[2:].upper()
    if vak.subjectCode in groepnaam:
        return f"{jaarnaam}{groepnaam}"
    else:
        return f"{jaarnaam}{vak.subjectCode}{groepnaam[-1]}"


def find_groepen(vak: Vak, groepen: Groepen) -> list[Groep]:
    result = []
    logger.debug(f"finding groep for vak: {vak.subjectCode}")
    for groep in groepen.get_department_groups(vak.departmentOfBranch):
        if groep in result:
            continue
        if vak.qualifiedCode and vak.qualifiedCode in groep.extendedName:
            logger.debug(
                f"found {groep.name} with {vak.qualifiedCode} in {groep.extendedName}"
            )
            result.append(groep)
    return result


def clean_docs(docs: list[str]) -> list[str]:
    checklist = list(set(docs))
    if "lgverv" in checklist:
        checklist.remove("lgverv")
    max = 0
    if len(checklist) > 1:
        logger.warning(f"multiple docs: {checklist}")
        for doc in checklist:
            doc_count = docs.count(doc)
            if doc_count > max:
                result = doc
                max = doc_count
        logger.warning(f"result: {result} ({max})")
        return [result]
    return checklist


@dataclass
class Les:
    id: int
    appointmentInstance: int
    teachers: list[str]
    students: list[str]
    subjects: list[str]
    groups: list[str]
    groupsInDepartments: list[int]
    choosableInDepartmentCodes: list[str]
    valid: bool
    cancelled: bool

    def filter(self, name: str) -> bool:
        if self.cancelled:
            return False
        if not self.valid:
            return False
        if len(self.students) > 40:
            logger.debug("groep te groot")
            return False
        if not any([name.split(".")[-1] in group for group in self.groups]):
            logger.debug(f"{name} not in {self}")
            return False
        return True


def get_vak_data(
    id: int, code: str, groupName: str, start, eind
) -> tuple[list[int], list[str], list[str]]:
    query = f"appointments/?containsStudentsFromGroupInDepartment={id}&subjects={code}&type=lesson&start={start}&end={eind}&fields=appointmentInstance,id,teachers,students,subjects,groups,groupsInDepartments,choosableInDepartmentCodes,valid,cancelled"
    vakdata = self.zermelo.load_query(query)
    grp_bck = []
    ll_bck = []
    doc_bck = []
    leerlingen = []
    docenten = []
    grp_namen = []
    lessen = [Les(**row) for row in reversed(vakdata) if row]
    for les in [les for les in lessen if les.filter(groupName)]:
        if len(les.groups) > 1:
            if not grp_namen and not grp_bck or len(les.groups) < len(grp_bck):
                logger.debug("meerdere groepen")
                grp_bck = les.choosableInDepartmentCodes
                ll_bck = list(set([llnr for llnr in les.students]))
                doc_bck = list(set([doc for doc in les.teachers]))
            continue
        if les.students and les.teachers:
            [leerlingen.append(llnr) for llnr in les.students if llnr not in leerlingen]
            [docenten.append(doc) for doc in les.teachers]
            [
                grp_namen.append(grp)
                for grp in les.choosableInDepartmentCodes
                if grp not in grp_namen
            ]
    if not grp_namen and grp_bck:
        logger.debug(f"result groepen: {grp_bck}")
        grp_namen = grp_bck
    if not docenten and doc_bck:
        logger.debug(f"result docenten: {doc_bck}")
        docenten = doc_bck
    if not leerlingen and ll_bck:
        logger.debug(f"result leerlingen: {ll_bck}")
        leerlingen = ll_bck
    docenten = clean_docs(docenten)
    leerlingen = [int(llnr) for llnr in leerlingen]
    return (leerlingen, docenten, grp_namen)


def find_deelnemers(
    vak: Vak, groep: Groep
) -> tuple[list[int], list[str], list[str]] | bool:
    date = get_date()
    try:
        logger.debug(groep)
        for x in [0, -1, -2, 1, 2, 3]:
            dweek = x * 4
            starttijd = int(delta_week(date, dweek).timestamp())
            eindtijd = int(delta_week(date, dweek + 4).timestamp())
            data = get_vak_data(
                groep.id, vak.subjectCode, groep.extendedName, starttijd, eindtijd
            )
            leerlingen, docenten, groep_namen = data
            if len(leerlingen) and len(docenten):
                logger.debug(f"found for {groep}")
                namen = [
                    groepnaam
                    for groepnaam in groep_namen
                    if vak.departmentOfBranchCode in groepnaam
                ]
                return (leerlingen, docenten, namen)
        if not len(leerlingen) or not len(docenten):
            logger.debug(f"geen deelnemers gevonden voor {groep}\n {vak}")
            return False
    except Exception as e:
        logger.error(e)
        return False


def get_info(
    llnrs: list[int],
    doc_codes: list[str],
    names: list[str],
    ll: Leerlingen,
    docs: Personeel,
) -> tuple[list[Leerling], list[Medewerker], list[str]]:
    leerlingen = [ll.get(llnr) for llnr in llnrs]
    docenten = [docs.get(code) for code in doc_codes]
    return (leerlingen, docenten, names)


@dataclass
class Lesgroep:
    vak: Vak
    groep: Groep
    leerjaar: Leerjaar
    leerlingen: list[Leerling] = field(default_factory=list)
    docenten: list[Medewerker] = field(default_factory=list)
    namen: list[str] = field(default_factory=list)
    naam: str = ""

    def __post_init__(self):
        self.naam = createLesgroepNaam(self.vak, self.groep)
        for leerling in self.leerlingen:
            leerling.leerjaren.add(self.leerjaar.id)


@dataclass
class Lesgroepen(list[Lesgroep]):
    leerjaren: InitVar
    vakken: InitVar
    groepen: InitVar
    leerlingen: InitVar
    personeel: InitVar

    def __post_init__(
        self,
        leerjaren: Leerjaren,
        vakken: Vakken,
        groepen: Groepen,
        leerlingen: Leerlingen,
        personeel: Personeel,
    ):
        for leerjaar in leerjaren:
            for vak in vakken.get_leerjaar_vakken(leerjaar.id):
                if vak.subjectType in ["education", "profile"] or vak.scheduleCode in [
                    "lo",
                    "sport",
                ]:
                    # skip educatio / profile / lo
                    continue
                logger.debug(vak)
                found = False
                for groep in find_groepen(vak, groepen):
                    groepinfo = find_deelnemers(vak, groep)
                    if groepinfo:
                        data = get_info(*groepinfo, leerlingen, personeel)
                        self.append(Lesgroep(vak, groep, leerjaar, *data))
                        found = True
                if found:
                    continue
                logger.debug(f"trying maingroups for {vak.subjectName}")
                for groep in groepen.get_department_groups(
                    vak.departmentOfBranch, True
                ):
                    logger.debug(f"trying: {groep}")
                    groepinfo = find_deelnemers(vak, groep)
                    if groepinfo:
                        data = get_info(*groepinfo, leerlingen, personeel)
                        self.append(Lesgroep(vak, groep, leerjaar, *data))
                        found = True
                if not found:
                    logger.warning(f"geen groepen gevonden voor {vak}")
        self.clean_leerlingen()
        logger.info(f"found {len(self)} lesgroepen")

    def clean_leerlingen(self):
        for lesgroep in self:
            for leerling in lesgroep.leerlingen.copy():
                if leerling.leerjaren.get_id() != lesgroep.leerjaar.id:
                    logger.warning(
                        f"removing leerling ({leerling.fullName}) from {lesgroep.naam}"
                    )
                    lesgroep.leerlingen.remove(leerling)
