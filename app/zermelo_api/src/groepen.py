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

    def get_department_groups(
        self, departmentOfBranch: int, maingroup: bool = False
    ) -> list[Groep]:
        # returns all groups (if it is/isnt stamklas (maingroup))
        return [
            groep
            for groep in self
            if groep.departmentOfBranch == departmentOfBranch
            and groep.isMainGroup == maingroup
        ]
