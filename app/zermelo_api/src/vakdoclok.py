from .zermelo_api import ZermeloCollection, zermelo
from dataclasses import dataclass, InitVar, field


@dataclass
class VakDocLokData:
    teachers: list[str]
    locationsOfBranch: list[int]  # lokalen
    choosableInDepartments: list[str]


class DataVakDocLoks(ZermeloCollection, list[VakDocLokData]):
    def __init__(self, id_branch: int, start: int, eind: int):
        query = f"appointments?branchOfSchool={id_branch}&fields=locationsOfBranch,teachers,choosableInDepartments,&start={start}&end={eind}"
        self.load_collection(query, VakDocLokData)


@dataclass
class VakDocLok:
    id: int
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
    def add(self, id) -> VakDocLok:
        vakdoclok = self.get(id)
        if not vakdoclok:
            vakdoclok = VakDocLok(id)
            self.append(vakdoclok)
        return vakdoclok

    def get(self, id: int) -> VakDocLok | bool:
        for vakdoclok in self:
            if vakdoclok.id == id:
                return vakdoclok
        return False


def get_vakdocloks(id_branch: int, start: int, eind: int):
    vakdata = DataVakDocLoks(id_branch, start, eind)
    vakdocloks = VakDocLoks()
    for data in vakdata:
        for id in data.choosableInDepartments:
            vakdoclok = vakdocloks.add(id)
            vakdoclok.add_docs(data.teachers)
            vakdoclok.add_loks(data.locationsOfBranch)
    return vakdocloks
