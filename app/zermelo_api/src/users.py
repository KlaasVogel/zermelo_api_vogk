from ._zermelo_collection import ZermeloCollection, from_zermelo_dict
from dataclasses import dataclass, InitVar, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class User:
    code: str
    roles: list[str]
    firstName: str
    prefix: str
    lastName: str
    schoolInSchoolYears: list[int]
    isApplicationManager: bool
    archived: bool
    isStudent: bool
    isEmployee: bool
    isFamilyMember: bool
    hasPassword: bool
    isSchoolScheduler: bool
    isSchoolLeader: bool
    isStudentAdministrator: bool
    isTeamLeader: bool
    isSectionLeader: bool
    isMentor: bool
    isParentTeacherNightScheduler: bool
    isDean: bool
    fullName: str = ""

    def __post_init__(self):
        self.fullName = self.generatename()

    def generatename(self) -> str:
        if self.prefix:
            fullname = " ".join(
                [self.firstName, self.prefix, self.lastName.split(",")[0]]
            )
        elif self.firstName is not None and self.lastName is not None:
            fullname = " ".join([self.firstName, self.lastName])
        elif self.lastName is not None:
            fullname = self.lastName
        else:
            fullname = "unknown"
        return fullname


class Users(list[User]):
    def print_list(self):
        return (
            f" = [" + ", ".join([str(user) for user in self]) + "]" if len(self) else ""
        )


@dataclass
class LeerjaarCounter:
    id: int
    count: int = 0


class LeerjaarCounters(list[LeerjaarCounter]):
    def get(self, id) -> LeerjaarCounter:
        for ljcounter in self:
            if ljcounter.id == id:
                return ljcounter
        self.append(LeerjaarCounter(id))
        return self[-1]

    def add(self, leerjaar_id: int):
        counter = self.get(leerjaar_id)
        counter.count += 1

    def get_id(self) -> int:
        if len(self):
            self.sort(key=lambda x: x.count, reverse=True)
            return self[0].id
        return 0


@dataclass
class Leerling(User):
    volgnr: int = 0
    leerjaren: LeerjaarCounters = field(default_factory=LeerjaarCounters)


@dataclass
class Leerlingen(Users, ZermeloCollection[Leerling]):
    schoolinschoolyear: InitVar[int] = 0

    def __post_init__(self, schoolinschoolyear: int):
        super().__post_init__()
        self.query = f"users?schoolInSchoolYear={schoolinschoolyear}&isStudent=true"
        self.type = Leerling

    async def _init(self):
        data = await self.get_collection()
        if data:
            self.load_leerlingen(data)

    def load_leerlingen(self, data: list[dict]):
        logger.info("loading Leerlingen")
        data.sort(key=lambda x: (x["lastName"], x["firstName"]))
        for idx, row in enumerate(data):
            self.append(from_zermelo_dict(Leerling, row, volgnr=idx + 1))
        logger.info(f"found: {len(self)} leerlingen")

    def __repr__(self):
        return f"{self}{self.print_list()}"

    def __str__(self):
        return f"Leerlingen({len(self)})"

    def get(self, llnr) -> Leerling:
        for user in self:
            if user.code == str(llnr):
                return user


@dataclass
class Medewerker(User):
    def __repr__(self):
        return self.fullName + f"({self.code})"


@dataclass
class Personeel(Users, ZermeloCollection[Medewerker]):
    schoolinschoolyear: InitVar[int] = 0

    def __post_init__(self, schoolinschoolyear: int):
        self.query = f"users?schoolInSchoolYear={schoolinschoolyear}&isEmployee=true"
        self.type = Medewerker

    def __repr__(self):
        return f"{self}{self.print_list()}"

    def __str__(self):
        return f"Personeel({len(self)})"

    def get(self, code: str):
        for user in self:
            if user.code == code:
                return user
