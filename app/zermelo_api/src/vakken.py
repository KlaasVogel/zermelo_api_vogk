from .zermelo_api import from_zermelo_dict, ZermeloCollection, zermelo
from .logger import makeLogger, DEBUG
from .groepen import Groepen, Groep
from dataclasses import dataclass, InitVar, field

logger = makeLogger("VAKKEN")


@from_zermelo_dict
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


@dataclass
class Vakken(ZermeloCollection, list[Vak]):
    schoolinschoolyear: InitVar
    groepen: InitVar

    def __post_init__(self, schoolinschoolyear: int, groepen: Groepen):
        query = f"choosableindepartments?schoolInSchoolYear={schoolinschoolyear}"
        self.load_collection(query, Vak)
        # [vak.find_groepen(groepen) for vak in self]

    def get_leerjaar_vakken(self, leerjaar_id: int) -> list[Vak]:
        return [vak for vak in self if vak.departmentOfBranch == leerjaar_id]
