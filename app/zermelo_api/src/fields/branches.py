from ..logger import makeLogger
from ..zermelo_api import ZermeloCollection, from_zermelo_dict, zermelo
from .users import Leerling, Leerlingen, Personeel, Medewerker
from .departments import Leerjaren, Leerjaar
from dataclasses import dataclass, InitVar, field


logger = makeLogger("BRANCH")


@from_zermelo_dict
@dataclass
class SchoolInSchoolYear:
    id: int
    # school: int
    # year: int
    # archived: bool
    # name: str
    # projectName: str
    # schoolName: str
    # schoolHrmsCode: str


@from_zermelo_dict
@dataclass
class Branch:
    id: int
    schoolInSchoolYear: int
    branch: str
    name: str
    schoolYear: int
    leerlingen: list[Leerling] = field(default_factory=list)
    personeel: list[Medewerker] = field(default_factory=list)
    leerjaren: list[Leerjaar] = field(default_factory=list)

    def __post_init__(self):
        logger.info(f"*** loading branch: {self.name} ***")
        self.leerlingen = Leerlingen(self.schoolInSchoolYear)
        self.personeel = Personeel(self.schoolInSchoolYear)
        self.leerjaren = Leerjaren(self.schoolInSchoolYear)


@dataclass
class Branches(ZermeloCollection, list[Branch]):
    year: InitVar

    def __post_init__(self, year: int = 2023):
        query = f"schoolsinschoolyears/?year={year}&archived=False"
        data = zermelo.load_query(query)
        for schoolrow in data:
            school = SchoolInSchoolYear(schoolrow)
            query = f"branchesofschools/?schoolInSchoolYear={school.id}"
            self.load_collection(query, Branch)

    def __str__(self):
        return "Branches(" + ", ".join([br.name for br in self]) + ")"
