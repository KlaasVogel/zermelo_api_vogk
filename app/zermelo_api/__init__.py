from .src._zermelo_api import ZermeloAPI, loadAPI
from .src.schoolyears import SchoolYears, SchoolInSchoolYear
from .src.branches import Branch, Branches, load_branches, load_schools
# from .src._time_utils import *
from .src.users import Leerling, Medewerker, Leerlingen, Personeel
from .src.lesgroepen import Lesgroepen, Lesgroep
from .src.leerjaren import Leerjaar, Leerjaren
from .src.appointments import get_user_appointments, get_department_updates, Appointment
from .src.vakken import Vakken, Vak
from .src.lokalen import Lokalen, Lokaal
from .src.vakdoclok import VakDocLoks, VakDocLok
