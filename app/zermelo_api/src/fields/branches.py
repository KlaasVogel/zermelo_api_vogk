from .fields import ZermeloField, ZermeloCollection, from_zermelo_dict
from dataclasses import dataclass, InitVar
from ..logger import makeLogger

logger = makeLogger("BRANCH")


@from_zermelo_dict
@dataclass
class SchoolInSchoolYear:
    id: int
    school: int
    year: int
    archived: bool
    name: str
    projectName: str
    schoolName: str
    schoolHrmsCode: str


@dataclass
class Branch(ZermeloField):
    schoolinschoolyear: InitVar

    def __post_init__(self, schoolinschoolyear: SchoolInSchoolYear):
        query = f"branchesofschools/?schoolInSchoolYear={schoolinschoolyear.id}"
        data = self.load(query)
        print(data)


@dataclass
class Branches(ZermeloCollection, list[Branch]):
    year: InitVar

    def __post_init__(self, year: int = 2023):
        query = f"schoolsinschoolyears/?year={year}&archived=False"
        data = self.load(query)
        for row in data:
            school = SchoolInSchoolYear(row)
            print(school)
            self.append(Branch(school))
