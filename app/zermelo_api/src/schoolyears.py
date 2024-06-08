from ._zermelo_api import loadAPI
from ._zermelo_collection import ZermeloCollection
from ._time_utils import get_year
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class SchoolInSchoolYear:
    id: int
    name: str
    school: int = field(repr=False)
    year: int = field(repr=False)
    archived: bool = field(repr=False)
    projectName: str = field(repr=False)
    schoolName: str = field(repr=False)
    schoolHrmsCode: str = field(repr=False)


@dataclass
class SchoolYears(ZermeloCollection[SchoolInSchoolYear]):
    def __post_init__(self, datestring: str = ""):
        year = get_year(datestring)
        logger.debug(year)
        self.query = f"schoolsinschoolyears/?year={year}&archived=False"
        self.type = SchoolInSchoolYear

    def __repr__(self):
        return f"SchoolYears([{super().__repr__()}])"


async def load_schoolyears(schoolname, date: str = "") -> SchoolYears:
    try:
        await loadAPI(schoolname)
        schoolyears = SchoolYears()
        await schoolyears._init(date)
        return schoolyears
    except Exception as e:
        logger.error(e)
