from ..zermelo_api import ZermeloAPI
from ..logger import makeLogger
from dataclasses import dataclass, InitVar
import inspect

logger = makeLogger("FIELDS")

zermelo = ZermeloAPI()

if not zermelo.checkCreds():
    with open("creds.ini") as f:
        token = f.read()
        zermelo.add_token(token)


def from_zermelo_dict(cls):
    def dict_checker(data: dict, *args, **kwargs):
        [
            logger.debug(f"{k} ({v}) not defined in {cls}")
            for k, v in data.items()
            if k not in inspect.signature(cls).parameters
        ]
        return cls(
            *args,
            **kwargs,
            **{k: v for k, v in data.items() if k in inspect.signature(cls).parameters},
        )

    return dict_checker


class Zermelo:
    def get_data(self, query: str) -> list[dict]:
        try:
            status, data = zermelo.getData(query)
            if status != 200:
                raise Exception(f"Error loading data {status}")
            if not data:
                logger.warning("no data")
        except Exception as e:
            # logger.trace()
            logger.debug(e)
            data = []
        return data


class ZermeloField(Zermelo):
    def load(self, query: str, **kwargs) -> dict:
        data = self.get_data(query)
        if not data:
            return {}
        logger.info(data)
        if len(data) > 1 and kwargs:
            for row in data:
                if all([row.get(k, None) == v for k, v in kwargs.items()]):
                    return row
        return data[0]


class ZermeloCollection(Zermelo):
    def load(self, query: str) -> list[dict]:
        return self.get_data(query)
