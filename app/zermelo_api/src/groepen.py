from .zermelo_api import from_zermelo_dict, ZermeloCollection
from .logger import makeLogger
from dataclasses import dataclass, InitVar


@from_zermelo_dict
@dataclass
class Groep:
    id: int
    isMainGroup: bool
    isMentorGroup: bool
    departmentOfBranch: int
    name: str
    extendedName: str


@dataclass
class Groepen(ZermeloCollection, list[Groep]):
    schoolinschoolyear: InitVar

    def __post_init__(self, schoolinschoolyear: int):
        query = f"groupindepartments?schoolInSchoolYear={schoolinschoolyear}"
        self.load_collection(query, Groep)
