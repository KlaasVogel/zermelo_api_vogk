from dataclasses import dataclass, field, InitVar
from .vakken import Vakken, Vak
from .groepen import Groepen, Groep
from .users import Leerlingen, Personeel
from .leerjaren import Leerjaren
from .time_utils import get_date, delta_week
from .logger import makeLogger, DEBUG
from .zermelo_api import zermelo

# from typing import Tuple

logger = makeLogger("LESGROEP")


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


def get_vak_data(
    id: int, code: str, start, eind
) -> tuple[list[int], list[str], list[str]]:
    query = f"appointments/?containsStudentsFromGroupInDepartment={id}&subjects={code}&type=lesson&start={start}&end={eind}&fields=appointmentInstance,id,teachers,students,subjects,groups,groupsInDepartments,choosableInDepartmentCodes,valid,cancelled"
    vakdata = zermelo.load_query(query)
    leerlingen = []
    docenten = []
    lesgroepen = []
    grp_bck = []
    ll_bck = []
    doc_bck = []
    for row in reversed(vakdata):
        if row["valid"] and not row["cancelled"] and code in row["subjects"]:
            logger.debug(f"get vak: {code}")
            logger.debug(f"groep: {id}")
            logger.debug(row)
            ll_data = row["students"]
            doc_data = row["teachers"]
            grp_data = row["choosableInDepartmentCodes"]
            if len(ll_data) > 40:
                logger.debug("groep te groot")
                continue
            if len(row["groups"]) > 1:
                if not lesgroepen and not grp_bck or len(row["groups"]) < len(grp_bck):
                    logger.warning("meerdere groepen")
                    grp_bck = grp_data
                    ll_bck = list(set([llnr for llnr in ll_data]))
                    doc_bck = list(set([doc for doc in doc_data]))
                continue
            if ll_data and doc_data:
                [leerlingen.append(llnr) for llnr in ll_data if llnr not in leerlingen]
                [docenten.append(doc) for doc in doc_data]
                [lesgroepen.append(grp) for grp in grp_data if grp not in lesgroepen]
    if not lesgroepen and grp_bck:
        logger.warning(f"result groepen: {grp_bck}")
        lesgroepen = grp_bck
    if not docenten and doc_bck:
        logger.warning(f"result docenten: {doc_bck}")
        docenten = doc_bck
    if not leerlingen and ll_bck:
        logger.warning(f"result leerlingen: {ll_bck}")
        leerlingen = ll_bck
    docenten = clean_docs(docenten)
    return (leerlingen, docenten, lesgroepen)


def find_deelnemers(vak: Vak, groep: Groep) -> tuple[list[int], list[str], list[str]]:
    date = get_date()
    try:
        for x in [0, -1, -2, 1, 2, 3]:
            dweek = x * 4
            starttijd = int(delta_week(date, dweek).timestamp())
            eindtijd = int(delta_week(date, dweek + 4).timestamp())
            data = get_vak_data(groep.id, vak.subjectCode, starttijd, eindtijd)
            leerlingen, docenten, groep_ids = data
            if len(leerlingen) and len(docenten):
                logger.debug(f"found for {groep}")
                break
        if not len(leerlingen) or not len(docenten):
            logger.debug(f"geen deelnemers gevonden voor {groep}\n {vak}")
    except Exception:
        logger.trace()
        data = ([], [], [])
    finally:
        return data


@dataclass
class Lesgroep:
    vak: Vak
    groep: Groep
    leerjaar: str
    naam: str = ""
    docenten: list[str] = field(default_factory=list)
    leerlingen: list[int] = field(default_factory=list)
    namen: list[str] = field(default_factory=list)
    lastcheck: int = 0

    def __post_init__(self):
        self.naam = createLesgroepNaam(self.vak, self.groep)


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
                logger.info(vak)
                for groep in find_groepen(vak, groepen):
                    logger.info(find_deelnemers(vak, groep))
