from .logger import makeLogger
from .zermelo_api import ZermeloCollection, zermelo, from_zermelo_dict
from .time_utils import get_date, get_year, datetime
from .users import Leerling, Leerlingen, Personeel, Medewerker
from .leerjaren import Leerjaren, Leerjaar
from .groepen import Groep, Groepen
from .lesgroepen import Lesgroepen, Lesgroep
from .vakken import Vakken, Vak
from dataclasses import dataclass, InitVar, field

# branch is roughly translated to 'afdeling' in Dutch
# for readability kept as branch, might be changed in the future

logger = makeLogger("BRANCH")


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


@dataclass
class Branch:
    id: int
    schoolInSchoolYear: int
    branch: str
    name: str
    schoolYear: int
    date: datetime = datetime.now()
    leerlingen: list[Leerling] = field(default_factory=list)
    personeel: list[Medewerker] = field(default_factory=list)
    leerjaren: list[Leerjaar] = field(default_factory=list)
    vakken: list[Vak] = field(default_factory=list)
    groepen: list[Groep] = field(default_factory=list)
    lesgroepen: list[Lesgroep] = field(default_factory=list)

    def __post_init__(self):
        logger.info(f"*** loading branch: {self.name} ***")
        self.leerlingen = Leerlingen(self.schoolInSchoolYear)
        self.personeel = Personeel(self.schoolInSchoolYear)
        self.leerjaren = Leerjaren(self.schoolInSchoolYear)
        self.groepen = Groepen(self.schoolInSchoolYear)
        self.vakken = Vakken(self.schoolInSchoolYear, self.groepen)

    def load_lesgroepen(self):
        if self.leerlingen and self.personeel:
            self.lesgroepen = Lesgroepen(
                self.leerjaren,
                self.vakken,
                self.groepen,
                self.leerlingen,
                self.personeel,
            )


@dataclass
class Branches(ZermeloCollection, list[Branch]):
    datestring: InitVar = ""

    def __post_init__(self, datestring):
        logger.debug("init branches")
        date = get_date(datestring)
        year = get_year(datestring)
        logger.debug(year)
        query = f"schoolsinschoolyears/?year={year}&archived=False"
        data = zermelo.load_query(query)
        for schoolrow in data:
            school = from_zermelo_dict(SchoolInSchoolYear, schoolrow)
            query = f"branchesofschools/?schoolInSchoolYear={school.id}"
            self.load_collection(query, Branch)
        for branch in self:
            branch.date = date

    def __str__(self):
        return "Branches(" + ", ".join([br.name for br in self]) + ")"

    def get(self, name: str) -> Branch:
        logger.info(f"loading branch: {name} ")
        for branch in self:
            if (
                name.lower() in branch.branch.lower()
                or branch.branch.lower() in name.lower()
            ):
                return branch
        else:
            logger.error(f"NO Branch found for {name}")
