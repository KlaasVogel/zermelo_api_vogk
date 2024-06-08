from dataclasses import dataclass, field, InitVar
from .vakken import Vakken, Vak
from .vaklessen import get_groep_data, LesData
from .groepen import Groepen, Groep
from .users import Leerlingen, Leerling, Personeel, Medewerker
from .leerjaren import Leerjaren, Leerjaar
from ._zermelo_collection import from_zermelo_dict
import asyncio
import logging

logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)


def createLesgroepNaam(vak: Vak, groep: Groep) -> str:
    leerjaar, groepnaam = groep.extendedName.split(".")
    jaarnaam = leerjaar[2:].upper()
    if vak.subjectCode in groepnaam:
        return f"{jaarnaam}{groepnaam}"
    else:
        return f"{jaarnaam}{vak.subjectCode}{groepnaam[-1]}"

def get_info(
    llnrs: list[int],
    doc_codes: list[str],
    names: list[str],
    ll: Leerlingen,
    docs: Personeel,
) -> tuple[list[Leerling], list[Medewerker], list[str]]:
    leerlingen = [ll.get(llnr) for llnr in llnrs]
    docenten = [docs.get(code) for code in doc_codes]
    return (leerlingen, docenten, names)


@dataclass
class Lesgroep:
    vak: Vak
    groep: Groep
    leerjaar: Leerjaar
    leerlingen: list[Leerling] = field(default_factory=list)
    docenten: list[Medewerker] = field(default_factory=list)
    namen: list[str] = field(default_factory=list)
    naam: str = ""

    def __post_init__(self):
        self.naam = createLesgroepNaam(self.vak, self.groep)
        for leerling in self.leerlingen:
            leerling.leerjaren.add(self.leerjaar.id)


class Lesgroepen(list[Lesgroep]):

    @classmethod
    async def create(
        cls,
        leerjaren: Leerjaren,
        vakken: Vakken,
        groepen: Groepen,
        leerlingen: Leerlingen,
        personeel: Personeel,
    ):
        self = cls()
        for leerjaar in leerjaren:
            tasks1 = []
            logger.info(f"finding lesgroepen for {leerjaar.code}")
            for vak in vakken.get_leerjaar_vakken(leerjaar.id, skip=True):
                logger.debug(vak)
                vakgroepen = groepen.get_vakgroepen(vak)
                tasks1.append(
                    asyncio.create_task(
                        find_lesgroepen(
                            leerjaar, vak, vakgroepen, leerlingen, personeel
                        )
                    )
                )
            results: list[tuple[Vak, list[Lesgroep]]] = await asyncio.gather(*tasks1)
            tasks2 = []
            for vak, lesgroepen in results:
                self.extend(lesgroepen)
                if not len(lesgroepen):
                    logger.debug(f"no regular groups found for {vak.subjectName}")
                    maingroepen = groepen.get_department_groups(leerjaar.id, True)
                    tasks2.append(
                        asyncio.create_task(
                            find_lesgroepen(
                                leerjaar, vak, maingroepen, leerlingen, personeel
                            )
                        )
                    )
            if not len(tasks2):
                logger.debug("alle groepen gevonden.")
                continue
            results: list[tuple[Vak, list[Lesgroep]]] = await asyncio.gather(*tasks2)
            for vak, lesgroepen in results:
                self.extend(lesgroepen)
                if not len(lesgroepen):
                    logger.warning(f"geen groepen gevonden voor {vak}")
        self.clean_leerlingen()
        return self

    def clean_leerlingen(self):
        for lesgroep in self:
            for leerling in lesgroep.leerlingen.copy():
                if leerling.leerjaren.get_id() != lesgroep.leerjaar.id:
                    logger.warning(
                        f"removing leerling ({leerling.fullName}) from {lesgroep.naam}"
                    )
                    lesgroep.leerlingen.remove(leerling)


async def find_lesgroepen(
    lj: Leerjaar,
    vak: Vak,
    grpn: list[Groep],
    lln: Leerlingen,
    docs: Personeel,
) -> tuple[Vak, list[Lesgroep]]:
    datalist = await asyncio.gather(
        *[get_groep_data(lln.zermelo, vak, groep) for groep in grpn]
    )
    lesgroepen: list[Lesgroep] = []
    for groep, lesdata in datalist:
        if lesdata:
            groepdata = get_info(*lesdata, lln, docs)
            lesgroepen.append(Lesgroep(vak, groep, lj, *groepdata))
    return (vak, lesgroepen)

    # if not len(datalist):
    #     datalist = await asyncio.gather(*[get_vakgroep_data(groepen.zermelo, vak, groep) for groep in groepen])


# async def load_lesgroepen(leerjaar: Leerjaar, vak: Vak, groepen, ) -> Lesgroep:
#     vakdata = await
#     if vakdata:
#         data =
#         return

#                 data = get_vak_data(

#                 )
#                  = data

#             if not len(leerlingen) or not len(docenten):
#                 logger.debug(f"geen deelnemers gevonden voor {groep}\n {vak}")
#                 return False
#         except Exception as e:
#             logger.error(e)
#             return False


### uit lesgroepen:
# groepinfo = await find_deelnemers(vak, groep)
#                     if groepinfo:
#                         data = get_info(*groepinfo, leerlingen, personeel)
#                         self.append(Lesgroep(vak, groep, leerjaar, *data))
#                         found = True
#                 if found:
#                     continue
#                 logger.debug(f"trying maingroups for {vak.subjectName}")
#                 for groep in groepen.get_department_groups(
#                     vak.departmentOfBranch, True
#                 ):
#                     logger.debug(f"trying: {groep}")
#                     groepinfo = find_deelnemers(vak, groep)
#                     if groepinfo:
#                         data = get_info(*groepinfo, leerlingen, personeel)
#                         self.append(Lesgroep(vak, groep, leerjaar, *data))
#                         found = True
#                 if not found:
#                     logger.warning(f"geen groepen gevonden voor {vak}")
#         self.clean_leerlingen()
#         logger.info(f"found {len(self)} lesgroepen")
#         return self
