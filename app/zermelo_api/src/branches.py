from ._zermelo_collection import ZermeloCollection, from_zermelo_dict
from ._zermelo_api import zermelo, loadAPI
from ._time_utils import get_date, get_year, datetime
from .users import Leerlingen, Personeel
from .leerjaren import Leerjaren
from .groepen import Groepen
from .lesgroepen import Lesgroepen
from .vakken import Vakken
from .lokalen import Lokalen
from .vakdoclok import get_vakdocloks, VakDocLoks
from dataclasses import dataclass, field, InitVar
import asyncio
import logging

logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)

@dataclass
class SchoolInSchoolYear:
    id: int
    school: int
    year: int
    archived: bool
    name: str
    projectName: str
    schoolName: str
    schoolHrmsCode: str


@dataclass
class SchoolYears(ZermeloCollection[SchoolInSchoolYear]):
    def __post_init__(self, datestring: str = ""):
        year = get_year(datestring)
        logger.debug(year)
        self.query = f"schoolsinschoolyears/?year={year}&archived=False"
        self.type = SchoolInSchoolYear


@dataclass
class Branch:
    id: int
    schoolInSchoolYear: int
    branch: str
    name: str
    schoolYear: int
    date: datetime = datetime.now()
    leerlingen: Leerlingen = field(default_factory=list)
    personeel: Personeel = field(default_factory=list)
    leerjaren: Leerjaren = field(default_factory=list)
    vakken: Vakken = field(default_factory=list)
    groepen: Groepen = field(default_factory=list)
    lokalen: Lokalen = field(default_factory=list)

    def __post_init__(self):
        logger.info(f"*** loading branch: {self.name} ***")
        self.leerlingen = Leerlingen(self.schoolInSchoolYear)
        self.personeel = Personeel(self.schoolInSchoolYear)
        self.leerjaren = Leerjaren(self.schoolInSchoolYear)
        self.groepen = Groepen(self.schoolInSchoolYear)
        self.vakken = Vakken(self.schoolInSchoolYear)
        self.lokalen = Lokalen(self.schoolInSchoolYear)

    async def _init(self):
        attrs = ["leerlingen", "personeel", "leerjaren", "groepen", "vakken", "lokalen"]
        await asyncio.gather(*[getattr(self, name)._init() for name in attrs])

    async def find_lesgroepen(self) -> Lesgroepen | bool:
        if self.leerlingen and self.personeel:
            return await Lesgroepen.create(
                self.leerjaren,
                self.vakken,
                self.groepen,
                self.leerlingen,
                self.personeel,
            )
        return False

    async def get_vak_doc_loks(self) -> VakDocLoks:
        start = int(self.date.timestamp())
        eind = start + 28 * 24 * 3600
        return await get_vakdocloks(self.id, start, eind)


@dataclass
class Branches(ZermeloCollection[Branch]):
    type: InitVar

    def __post_init__(self, type=None):
        self.type = Branch if not type else type
        self.query = "branchesofschools/"

    async def _init(self, schoolyears: SchoolYears, datestring: str = ""):
        logger.debug("init branches")
        date = get_date(datestring)
        await asyncio.gather(
            *[self.load_from_schoolyear(sy, date) for sy in schoolyears]
        )
        await asyncio.gather(*[branch._init() for branch in self])
        logger.info(self)

    async def load_from_schoolyear(self, sy: SchoolInSchoolYear, date: datetime):
        query = f"branchesofschools/?schoolInSchoolYear={sy.id}"
        await self.load_collection(query, date=date)

    def __str__(self):
        return "Branches(" + ", ".join([br.name for br in self]) + ")"

    def get(self, name: str) -> Branch:
        for branch in self:
            if (
                name.lower() in branch.branch.lower()
                or branch.branch.lower() in name.lower()
            ):
                return branch
        else:
            logger.error(f"NO Branch found for {name}")


async def load_branches(schoolname: str, date: str = "", type=None) -> Branches:
    try:
        _, branches = await load_schools(schoolname, date, type)
        return branches
    except Exception as e:
        logger.error(e)


async def load_schoolyears(schoolname, date: str = "") -> SchoolYears:
    try:
        await loadAPI(schoolname)
        schoolyears = SchoolYears()
        await schoolyears._init(date)
        return schoolyears
    except Exception as e:
        logger.error(e)


async def load_schools(
    schoolname, date: str = "", type=None
) -> tuple[SchoolYears, Branches]:
    try:
        schoolyears = await load_schoolyears(schoolname, date)
        branches = Branches(type=type)
        await branches._init(schoolyears, date)
        return (schoolyears, branches)
    except Exception as e:
        logger.error(e)
