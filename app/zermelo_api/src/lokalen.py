from ._zermelo_collection import ZermeloCollection
from dataclasses import dataclass, InitVar, field
import logging

logger = logging.getLogger(__name__)

@dataclass
class Lokaal:
    id: int
    name: str
    parentteachernightCapacity: int
    courseCapacity: int
    supportsConcurrentAppointments: bool
    allowMeetings: bool
    branchOfSchool: int
    secondaryBranches: list[int]
    schoolInSchoolYear: int


@dataclass
class Lokalen(ZermeloCollection[Lokaal]):
    schoolinschoolyear: InitVar[int] = 0

    def __post_init__(self, schoolinschoolyear: int):
        self.query = f"locationofbranches?schoolInSchoolYear={schoolinschoolyear}"
        # self.type = Lokaal

    def get(self, id: int) -> Lokaal | None:
        for lokaal in self:
            if lokaal.id == id:
                return lokaal
