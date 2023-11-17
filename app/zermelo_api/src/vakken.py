from .zermelo_api import from_zermelo_dict, ZermeloCollection
from .logger import makeLogger
from dataclasses import dataclass, InitVar


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

    def __post_init__(self, schoolinschoolyear: int):
        query = f"choosableindepartments?schoolInSchoolYear={schoolinschoolyear}"
        self.load_collection(query, Vak)

        for vak in self:
            print(vak)
