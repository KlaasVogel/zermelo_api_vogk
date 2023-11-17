from .zermelo_api import from_zermelo_dict, ZermeloCollection, zermelo
from .logger import makeLogger
from dataclasses import dataclass, InitVar

logger = makeLogger("GROEPEN")


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

    def get_department_groups(self, departmentOfBranch: int) -> list[Groep]:
        return [
            groep for groep in self if groep.departmentOfBranch == departmentOfBranch
        ]

    def get_main_groups(self, departmentOfBranch: int) -> list[Groep]:
        return [
            groep
            for groep in self.get_department_groups(departmentOfBranch)
            if groep.isMainGroup
        ]
