from .credentials import Credentials
from .logger import makeLogger
import json
import requests

logger = makeLogger("ZermeloAPI")

ZERMELO_NAME = "carmelhengelo"


class ZermeloAPI:
    def __init__(self, school=ZERMELO_NAME):
        self.credentials = Credentials()
        self.zerurl = f"https://{school}.zportal.nl/api/v3/"
        self.starttijd = 0
        self.eindtijd = 1

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

    def setTimes(self, start, end):
        logger.debug(f"start: {start}, end: {end}")
        self.starttijd = start
        self.eindtijd = end

    def getName(self):
        if not self.credentials.token:
            raise Exception("No Token loaded!")
        data = self.getData("users/~me", False)
        if not len(data):
            raise Exception("could not load user data with token")
        logger.debug(f"get name: {data[0]}")
        row = data[0]
        if not row["prefix"]:
            return " ".join([row["firstName"], row["lastName"]])
        else:
            return " ".join([row["firstName"], row["prefix"], row["lastName"]])

    def getData(self, task, with_id=True) -> list[dict]:
        # logger.debug("getting data from Zermelo:")
        data = {}
        try:
            request = (
                self.zerurl + task + f"&access_token={self.credentials.token}"
                if with_id
                else self.zerurl + task + f"?access_token={self.credentials.token}"
            )
            logger.debug(request)
            json_response = requests.get(request).json()
            if json_response:
                if json_response["response"]["status"] == 200:
                    data = json_response["response"]["data"]
                else:
                    logger.debug(
                        f"oeps, geen juiste response: {task}: {json_response['response']['status']} - {json_response['response']['details']}"
                    )
            else:
                logger.error("JSON - response is leeg")
        except Exception as e:
            logger.trace()
            logger.error(e)
        finally:
            return data
