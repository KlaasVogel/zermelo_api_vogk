from .zermelo_api import ZermeloCollection, zermelo
from .logger import makeLogger, DEBUG
from .groepen import Groepen, Groep
from dataclasses import dataclass, InitVar, field

logger = makeLogger("VAKKEN")


@dataclass
class Vak:
    id: int
    subject: int
    departmentOfBranch: int
    studentCanEdit: bool
    sectionOfBranch: int
    courseType: str
    lessonHoursInClassPeriods: list[dict]
    excludedSegments: list[int]
    referenceWeek: dict  # (year:int, weekNumber: int, schoolYear: int)
    isExam: bool
    scheduleCode: str
    subjectType: str
    subjectCode: str
    departmentOfBranchCode: str
    iltCode: int
    qualifiedCode: str
    subjectScheduleCode: str
    subjectName: str
    sectionOfBranchAbbreviation: str

    def getName(self) -> str:
        if "/" in self.subjectName:
            logger.debug(f"old name: {self.subjectName}")
            parts = self.subjectName.split("/")
            frontpart = parts[0]
            nameparts = frontpart.split(" ")
            nameparts.pop(-1)
            name = " ".join(nameparts)
            logger.debug(f"new name: {name}")
            return name.strip()
        return self.subjectName.strip()


@dataclass
class VakDocLokData:
    subjects: list[str]
    teachers: list[str]
    locationsOfBranch: list[str]  # lokalen


@dataclass
class DataVakDocLoks(ZermeloCollection, list[VakDocLokData]):
    id_branch: InitVar
    start: InitVar
    eind: InitVar

    def __post_init__(self, id_branch: int, start: int, eind: int):
        query = f"appointments?branchOfSchool={id_branch}&fields=locationsOfBranch,subjects,teachers&start={start}&end={eind}"
        self.load_collection(query, VakDocLokData)


@dataclass
class VakDocLok:
    vak: Vak
    docenten: list[str] = field(default_factory=list)
    lokalen: list[str] = field(default_factory=list)


@dataclass
class VakDocLoks(list[VakDocLok]):
    vakken: InitVar
    vakdata: InitVar

    def __post_init__(self, vakken: list[Vak], vakdata: DataVakDocLoks):
        for data in vakdata:
            for vaknaam in data.subjects:
                vak = vakken.get(vaknaam)


@dataclass
class Vakken(ZermeloCollection, list[Vak]):
    schoolinschoolyear: InitVar

    def __post_init__(self, schoolinschoolyear: int):
        query = f"choosableindepartments?schoolInSchoolYear={schoolinschoolyear}"
        self.load_collection(query, Vak)

    def get(self, vaknaam: str) -> Vak:
        for vak in self:
            if vak.subjectCode == vaknaam:
                return vak

    def get_leerjaar_vakken(self, leerjaar_id: int) -> list[Vak]:
        return [vak for vak in self if vak.departmentOfBranch == leerjaar_id]

    def get_vak_docent_lokaal(self, id_branch: int, start: int, eind: int):
        vakdata = DataVakDocLoks(id_branch, start, eind)
        [logger.info(vak) for vak in self]
        [logger.info(vak) for vak in vakdata]
        # return VakDocLoks(self, vakdata)
