from .zermelo_collection import ZermeloCollection, ZermeloAPI, from_zermelo_dict
from .time_utils import get_date, get_year, datetime
from .users import Leerlingen, Personeel
from .leerjaren import Leerjaren
from .groepen import Groepen

# from .lesgroepen import Lesgroepen
from .vakken import Vakken
from .lokalen import Lokalen

# from .vakdoclok import get_vakdocloks, VakDocLoks
from dataclasses import dataclass, InitVar, field
import asyncio
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

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
class Branch:
    zermelo: InitVar
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

    def __post_init__(self, zermelo: ZermeloAPI):
        logger.info(f"*** loading branch: {self.name} ***")
        self.leerlingen = Leerlingen(zermelo, self.schoolInSchoolYear)
        self.personeel = Personeel(zermelo, self.schoolInSchoolYear)
        self.leerjaren = Leerjaren(zermelo, self.schoolInSchoolYear)
        self.groepen = Groepen(zermelo, self.schoolInSchoolYear)
        self.vakken = Vakken(zermelo, self.schoolInSchoolYear)
        self.lokalen = Lokalen(zermelo, self.schoolInSchoolYear)

    async def _init(self):
        attrs = ["leerlingen", "personeel", "leerjaren", "groepen", "vakken", "lokalen"]
        await asyncio.gather(*[getattr(self, name)._init() for name in attrs])

    # def find_lesgroepen(self) -> Lesgroepen | bool:
    #     if self.leerlingen and self.personeel:
    #         return Lesgroepen(
    #             self.leerjaren,
    #             self.vakken,
    #             self.groepen,
    #             self.leerlingen,
    #             self.personeel,
    #         )
    #     return False

    # def get_vak_doc_loks(self, start: int, eind: int) -> VakDocLoks:
    #     return get_vakdocloks(self.id, start, eind)


@dataclass
class Branches(ZermeloCollection[Branch]):

    def __post_init__(self):
        super().__post_init__()
        self.type = Branch

    async def _init(self, datestring):
        logger.debug("init branches")
        date = get_date(datestring)
        year = get_year(datestring)
        logger.debug(year)
        query = f"schoolsinschoolyears/?year={year}&archived=False"
        data = await self.get_collection(query)
        tasks = []

        for schoolrow in data:
            school = from_zermelo_dict(SchoolInSchoolYear, schoolrow)
            query = f"branchesofschools/?schoolInSchoolYear={school.id}"
            tasks.append(
                asyncio.create_task(
                    self.load_collection(query, zermelo=self.zermelo, date=date)
                )
            )
        await asyncio.gather(*tasks)
        await asyncio.gather(*[branch._init() for branch in self])
        logger.info(self)

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
