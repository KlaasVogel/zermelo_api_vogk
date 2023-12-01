from .credentials import Credentials
from .logger import makeLogger, DEBUG, INFO
import json
import requests
import inspect

logger = makeLogger("ZermeloAPI")

ZERMELO_NAME = "carmelhengelo"


class ZermeloAPI:
    def __init__(self, school=ZERMELO_NAME):
        self.credentials = Credentials()
        self.zerurl = f"https://{school}.zportal.nl/api/v3/"

    def login(self, code: str) -> bool:
        token = self.get_access_token(code)
        return self.add_token(token)

    def get_access_token(self, code: str) -> str:
        token = ""
        url = self.zerurl + "oauth/token"
        # headers = {"Content-Type": "application/json"}
        zerrequest = requests.post(
            url, data={"grant_type": "authorization_code", "code": code}
        )
        if zerrequest.status_code == 200:
            data = json.loads(zerrequest.text)
            if "access_token" in data:
                token = data["access_token"]
        return token

    def add_token(self, token: str) -> bool:
        if not token:
            return False
        self.credentials.settoken(token)
        return self.checkCreds()

    def checkCreds(self):
        result = False
        try:
            self.getName()
            result = True
        except Exception as e:
            logger.trace()
            logger.error(e)
        finally:
            return result

    def getName(self):
        if not self.credentials.token:
            raise Exception("No Token loaded!")
        status, data = self.getData("users/~me", True)
        if status != 200 or not len(data):
            raise Exception("could not load user data with token")
        logger.debug(f"get name: {data[0]}")
        row = data[0]
        if not row["prefix"]:
            return " ".join([row["firstName"], row["lastName"]])
        else:
            return " ".join([row["firstName"], row["prefix"], row["lastName"]])

    def getData(self, task, from_id=False) -> tuple[int, list[dict]]:
        result = (500, [])
        try:
            request = (
                self.zerurl + task + f"?access_token={self.credentials.token}"
                if from_id
                else self.zerurl + task + f"&access_token={self.credentials.token}"
            )
            logger.debug(request)
            json_response = requests.get(request).json()
            if json_response:
                json_status = json_response["response"]["status"]
                if json_status == 200:
                    result = (200, json_response["response"]["data"])
                    logger.debug("    **** JSON OK ****")
                else:
                    logger.debug(
                        f"oeps, geen juiste response: {task}: {json_response['response']}"
                    )
                    result = (json_status, [])
            else:
                logger.error("JSON - response is leeg")
        except Exception as e:
            logger.trace()
        finally:
            return result

    def load_query(self, query: str) -> list[dict]:
        try:
            status, data = self.getData(query)
            if status != 200:
                raise Exception(f"Error loading data {status}")
            if not data:
                logger.debug("no data")
        except Exception as e:
            logger.debug(e)
            data = []
        return data


zermelo = ZermeloAPI()

if not zermelo.checkCreds():
    with open("creds.ini") as f:
        token = f.read()
        zermelo.add_token(token)


def from_zermelo_dict(cls, data: dict, *args, **kwargs):
    [
        logger.debug(f"{k} ({v}) not defined in {cls}")
        for k, v in data.items()
        if k not in inspect.signature(cls).parameters
    ]
    return cls(
        *args,
        **{k: v for k, v in data.items() if k in inspect.signature(cls).parameters},
        **kwargs,
    )


class ZermeloCollection:
    def load_collection(self: list, query: str, type: object) -> None:
        data = zermelo.load_query(query)
        for row in data:
            self.append(from_zermelo_dict(type, row))

    def test(self: list, query: str):
        data = zermelo.load_query(query)
        for row in data:
            logger.info(f"test: {row}")
