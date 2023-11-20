from .zermelo_api import from_zermelo_dict, ZermeloCollection, zermelo
from .logger import makeLogger
from dataclasses import dataclass, InitVar, field

logger = makeLogger("USERS")


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
            f" = [" + ", ".join([u.fullName for u in self]) + "]" if len(self) else ""
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


@from_zermelo_dict
@dataclass
class Leerling(User):
    volgnr: int = 0
    leerjaren: LeerjaarCounters = field(default_factory=LeerjaarCounters)


@dataclass
class Leerlingen(ZermeloCollection, Users, list[Leerling]):
    schoolinschoolyear: InitVar

    def __init__(self, schoolinschoolyear: int):
        query = f"users?schoolInSchoolYear={schoolinschoolyear}&isStudent=true"
        data = zermelo.load_query(query)
        if data:
            self.load_leerlingen(data)

    def load_leerlingen(self, data: list[dict]):
        logger.info("loading Leerlingen")
        data.sort(key=lambda x: (x["lastName"], x["firstName"]))
        for idx, row in enumerate(data):
            self.append(Leerling(row, volgnr=idx + 1))
        logger.info(f"found: {len(self)} leerlingen")

    def __repr__(self):
        return f"{self}{self.print_list()}"

    def __str__(self):
        return f"Leerlingen({len(self)})"

    def get(self, llnr) -> Leerling:
        for user in self:
            if user.code == str(llnr):
                return user


@from_zermelo_dict
@dataclass
class Medewerker(User):
    ...


@dataclass
class Personeel(ZermeloCollection, Users, list[Medewerker]):
    schoolinschoolyear: InitVar

    def __init__(self, schoolinschoolyear: int):
        query = f"users?schoolInSchoolYear={schoolinschoolyear}&isEmployee=true"
        self.load_collection(query, Medewerker)

    def __repr__(self):
        return f"{self}{self.print_list()}"

    def __str__(self):
        return f"Personeel({len(self)})"

    def get(self, code: str):
        for user in self:
            if user.code == code:
                return user
