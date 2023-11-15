from .credentials import Credentials
from .logger import makeLogger, DEBUG
import json
import requests
from traceback import format_exc

logger = makeLogger("ZermeloAPI", DEBUG)

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
            logger.error(format_exc())
            logger.error(e)
        finally:
            return result

    def getName(self):
        if not self.credentials.token:
            raise Exception("No Token loaded!")
        status, data = self.getData("users/~me", False)
        if status != 200 or not len(data):
            raise Exception("could not load user data with token")
        logger.debug(f"get name: {data[0]}")
        row = data[0]
        if not row["prefix"]:
            return " ".join([row["firstName"], row["lastName"]])
        else:
            return " ".join([row["firstName"], row["prefix"], row["lastName"]])

    def getData(self, task, with_id=True) -> tuple[int, list[dict]]:
        result = (500, [])
        try:
            request = (
                self.zerurl + task + f"&access_token={self.credentials.token}"
                if with_id
                else self.zerurl + task + f"?access_token={self.credentials.token}"
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
            logger.error(format_exc())
        finally:
            return result
