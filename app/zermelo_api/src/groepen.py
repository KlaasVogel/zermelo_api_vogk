from .zermelo_collection import ZermeloCollection
from dataclasses import dataclass, InitVar
import logging

logger = logging.getLogger(__name__)


@dataclass
class Groep:
    id: int
    isMainGroup: bool
    isMentorGroup: bool
    departmentOfBranch: int
    name: str
    extendedName: str


@dataclass
class Groepen(ZermeloCollection[Groep]):
    schoolinschoolyear: InitVar[int] = 0

    def __post_init__(self, schoolinschoolyear: int):
        self.query = f"groupindepartments?schoolInSchoolYear={schoolinschoolyear}"
        self.type = Groep

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
