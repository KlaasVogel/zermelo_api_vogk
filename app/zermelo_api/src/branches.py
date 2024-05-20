from .zermelo_api import ZermeloCollection, ZermeloAPI, from_zermelo_dict
from .time_utils import get_date, get_year, datetime
from .users import Leerling, Leerlingen, Personeel, Medewerker
from .leerjaren import Leerjaren, Leerjaar
from .groepen import Groep, Groepen
from .lesgroepen import Lesgroepen, Lesgroep
from .vakken import Vakken, Vak
from .lokalen import Lokalen, Lokaal
from .vakdoclok import get_vakdocloks, VakDocLoks
from dataclasses import dataclass, InitVar, field
import asyncio
import logging

# branch is roughly translated to 'afdeling' in Dutch
# for readability kept as branch, might be changed in the future

logger = logging.getLogger(__name__)

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
        self.leerlingen = Leerlingen(zermelo)
        self.personeel = Personeel(zermelo)
        self.leerjaren = Leerjaren(zermelo)
        self.groepen = Groepen(zermelo)
        self.vakken = Vakken(zermelo)
        self.lokalen = Lokalen(zermelo)

    async def _init(self):
        attrs = ["leerlingen", "personeel", "leerjaren", "groepen", "vakken", "lokalen"]
        id = self.schoolInSchoolYear
        await asyncio.gather(*[getattr(self, name)._init(id) for name in attrs])

    def find_lesgroepen(self) -> Lesgroepen | bool:
        if self.leerlingen and self.personeel:
            return Lesgroepen(
                self.leerjaren,
                self.vakken,
                self.groepen,
                self.leerlingen,
                self.personeel,
            )
        return False

    def get_vak_doc_loks(self, start: int, eind: int) -> VakDocLoks:
        return get_vakdocloks(self.id, start, eind)


class Branches(ZermeloCollection, list[Branch]):

    async def _init(self, datestring):
        logger.debug("init branches")
        date = get_date(datestring)
        year = get_year(datestring)
        logger.debug(year)
        query = f"schoolsinschoolyears/?year={year}&archived=False"
        data = await self.zermelo.load_query(query)

        for schoolrow in data:
            school = from_zermelo_dict(SchoolInSchoolYear, schoolrow)
            query = f"branchesofschools/?schoolInSchoolYear={school.id}"
            # self.load_collection(query, Branch, self.zermelo)
        # for branch in self:
        #     branch.date = date

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
