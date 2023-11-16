from ..zermelo_api import from_zermelo_dict, ZermeloCollection
from ..logger import makeLogger
from dataclasses import dataclass, InitVar

logger = makeLogger("DEPARTMENTS")


@from_zermelo_dict
@dataclass
class Leerjaar:
    id: int
    code: str
    yearOfEducation: int
    branchOfSchool: int
    teacherTeams: list[int]
    mainGroupAuthority: str
    educationType: str
    weekTimeTable: int
    teachingLevel: str
    educations: list[int]
    schoolInSchoolYear: int
    branchOfSchoolCode: str
    schoolInSchoolYearName: str
    profiles: list[int]
    schoolInSchoolYearId: int


@dataclass
class Leerjaren(ZermeloCollection, list[Leerjaar]):
    schoolinschoolyear: InitVar

    def __post_init__(self, schoolinschoolyear: int):
        query = f"departmentsofbranches?schoolInSchoolYear={schoolinschoolyear}"
        self.load_collection(query, Leerjaar)
