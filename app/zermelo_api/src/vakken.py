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
class Vakken(ZermeloCollection, list[Vak]):
    schoolinschoolyear: InitVar

    def __post_init__(self, schoolinschoolyear: int):
        query = f"choosableindepartments?schoolInSchoolYear={schoolinschoolyear}"
        self.load_collection(query, Vak)

    def get_leerjaar_vakken(self, leerjaar_id: int) -> list[Vak]:
        return [vak for vak in self if vak.departmentOfBranch == leerjaar_id]
