from .zermelo_collection import ZermeloCollection, ZermeloAPI
from .vakken import Vak
from .groepen import Groep
from .time_utils import get_date, delta_week
from dataclasses import dataclass, InitVar, field
import asyncio
import logging

logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)


@dataclass
class VakLes:
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
        if not len(self.students):
            return False
        if not len(self.teachers):
            return False
        if len(self.students) > 40:
            logger.debug("groep te groot")
            return False
        if not any([name.split(".")[-1] in group for group in self.groups]):
            logger.debug(f"{name} not in {self}")
            return False
        return True


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


class LesData(tuple[list[int], list[str], list[str]]): ...


@dataclass
class VakLessen(ZermeloCollection[VakLes]):
    id: InitVar[int] = 0
    code: InitVar[str] = ""
    groupName: str = ""
    start: InitVar[int] = 0
    eind: InitVar[int] = 0

    def __post_init__(self, id: int, code: str, start: int, eind: int):
        self.query = f"appointments/?containsStudentsFromGroupInDepartment={id}&subjects={code}&type=lesson&start={start}&end={eind}&fields=appointmentInstance,id,teachers,students,subjects,groups,groupsInDepartments,choosableInDepartmentCodes,valid,cancelled"
        self.type = VakLes

    def filter(self) -> list[VakLes]:
        return [les for les in self if les.filter(self.groupName)]

    def get_data(self) -> LesData:
        grp_bck = []
        ll_bck = []
        doc_bck = []
        leerlingen = []
        docenten = []
        grp_namen = []
        for les in self.filter():
            if len(les.groups) > 1:
                if not grp_namen and (not grp_bck or len(les.groups) < len(grp_bck)):
                    logger.debug("meerdere groepen")
                    grp_bck = les.choosableInDepartmentCodes
                    ll_bck = list(set([llnr for llnr in les.students]))
                    doc_bck = list(set([doc for doc in les.teachers]))
                continue
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


async def get_vakgroep_lessen(zermelo: ZermeloAPI, vak: Vak, groep: Groep) -> VakLessen:
    date = get_date()
    result: list[VakLessen] = []
    try:
        logger.debug(groep)
        for x in [0, -1, -2, 1, 2, 3]:
            dweek = x * 4
            starttijd = int(delta_week(date, dweek).timestamp())
            eindtijd = int(delta_week(date, dweek + 4).timestamp())
            result.append(
                VakLessen(
                    zermelo,
                    groep.id,
                    vak.subjectCode,
                    groep.extendedName,
                    starttijd,
                    eindtijd,
                )
            )
        for vaklessen in result:
            logger.debug(f"init: {vaklessen}")
            await vaklessen._init()
            if not len(vaklessen):
                logger.debug("geen lessen gevonden")
                continue
            lessen = vaklessen.filter()
            logger.debug(f"lessen: {lessen}")
            if len(lessen):
                return vaklessen
        logger.debug("geen valid vaklessen gevonden.")
    except Exception as e:
        logger.error(e)
    return []


def check_data(data: LesData, vak: Vak) -> LesData | bool:
    leerlingen, docenten, groep_namen = data
    if len(leerlingen) and len(docenten):
        namen = [
            groepnaam
            for groepnaam in groep_namen
            if vak.departmentOfBranchCode in groepnaam
        ]
        return (leerlingen, docenten, namen)
    return False


async def get_vakgroep_data(zermelo: ZermeloAPI, vak, groep) -> LesData | bool:
    vaklessen = await get_vakgroep_lessen(zermelo, vak, groep)
    if not len(vaklessen):
        logger.debug("geen lessen")
        return False
    logger.debug(f"vaklessen: {vaklessen}")
    lesdata = vaklessen.get_data()
    return check_data(lesdata, vak)


async def get_groep_data(
    zermelo: ZermeloAPI, vak: Vak, groep: Groep
) -> tuple[Groep, LesData | bool]:
    data = await get_vakgroep_data(zermelo, vak, groep)
    return (groep, data)
