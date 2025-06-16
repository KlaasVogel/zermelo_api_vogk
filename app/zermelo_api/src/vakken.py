from ._zermelo_collection import ZermeloCollection
from dataclasses import dataclass, InitVar, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class Vak:
    id: int
    subject: int
    departmentOfBranch: int
    studentCanEdit: bool
    sectionOfBranch: int
    courseType: str
    lessonHoursInClassPeriods: list[dict]
    scroungeSegments: list[int]
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
class Vakken(ZermeloCollection[Vak]):
    schoolinschoolyear: InitVar[int] = 0

    def __post_init__(self, schoolinschoolyear: int):
        self.query = f"choosableindepartments?schoolInSchoolYear={schoolinschoolyear}"
        # self.type = Vak

    def get(self, vaknaam: str) -> Vak | None:
        for vak in self:
            if vak.subjectCode == vaknaam:
                return vak

    def get_subject(self, subject: str) -> tuple[int, str]:
        """returns (code, naam)"""
        for vak in self:
            if vak.subjectCode == subject:
                return (vak.subject, vak.getName())
        return (0, "Onbekend")

    def get_leerjaar_vakken(self, leerjaar_id: int, skip: bool = False) -> list[Vak]:
        return [
            vak
            for vak in self
            if vak.departmentOfBranch == leerjaar_id
            and not (
                skip
                and (
                    vak.subjectType in ["education", "profile"]
                    or vak.scheduleCode
                    in [
                        "lo",
                        "sport",
                    ]
                )
            )
        ]
