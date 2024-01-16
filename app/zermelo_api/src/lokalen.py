from .zermelo_api import ZermeloCollection, zermelo
from .logger import makeLogger, DEBUG
from dataclasses import dataclass, InitVar, field

logger = makeLogger("LOKALEN")


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
class Lokalen(ZermeloCollection, list[Lokaal]):
    schoolInSchoolYear: InitVar

    def __post_init__(self, schoolInSchoolYear: int):
        query = f"locationofbranches?schoolInSchoolYear={schoolInSchoolYear}"
        self.load_collection(query, Lokaal)

    def get(self, id: int) -> Lokaal | None:
        for lokaal in self:
            if lokaal.id == id:
                return lokaal
