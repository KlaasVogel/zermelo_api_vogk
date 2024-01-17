from .zermelo_api import ZermeloCollection, zermelo
from .logger import makeLogger, DEBUG
from .vakken import Vakken
from .users import Personeel, Medewerker
from .lokalen import Lokalen, Lokaal
from dataclasses import dataclass, InitVar, field


@dataclass
class VakDocLokData:
    subjects: list[str]
    teachers: list[str]
    locationsOfBranch: list[int]  # lokalen


class DataVakDocLoks(ZermeloCollection, list[VakDocLokData]):
    def __init__(self, id_branch: int, start: int, eind: int):
        query = f"appointments?branchOfSchool={id_branch}&fields=locationsOfBranch,subjects,teachers&start={start}&end={eind}"
        self.load_collection(query, VakDocLokData)


@dataclass
class VakDocLok:
    subjectCode: str
    docenten: list[str] = field(default_factory=list)
    lokalen: list[int] = field(default_factory=list)

    def add_docs(self, docenten: list[str]):
        for doc in docenten:
            if doc not in self.docenten:
                self.docenten.append(doc)

    def add_loks(self, lokalen: list[int]):
        for lok in lokalen:
            if lok not in self.lokalen:
                self.lokalen.append(lok)


@dataclass
class VakDocLoks(list[VakDocLok]):
    def add(self, code) -> VakDocLok:
        vakdoclok = self.get(code)
        if not vakdoclok:
            vakdoclok = VakDocLok(code)
            self.append(vakdoclok)
        return vakdoclok

    def get(self, code: str) -> VakDocLok | bool:
        for vakdoclok in self:
            if vakdoclok.subjectCode == code:
                return vakdoclok
        return False


def get_vakdocloks(id_branch: int, start: int, eind: int):
    vakdata = DataVakDocLoks(id_branch, start, eind)
    vakdocloks = VakDocLoks()
    for data in vakdata:
        for subject in data.subjects:
            vakdoclok = vakdocloks.add(subject)
            vakdoclok.add_docs(data.teachers)
            vakdoclok.add_loks(data.locationsOfBranch)
    return vakdocloks
