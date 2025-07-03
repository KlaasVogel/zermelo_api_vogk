from ._config import getConfig
import logging

logger = logging.getLogger(__name__)


class Credentials:
    def __init__(self):
        self.file = getConfig("creds")
        self.schoolname = ""
        self.token = ""
        self.load()

    def load(self):
        try:
            data = self.file.load()
            self.schoolname = data["schoolname"]
            self.token = data["token"]
        except Exception as e:
            logger.error(e)
        finally:
            logger.debug(f"schoolname: {self.schoolname}")
            logger.debug(f"token: {self.token}")

    def check(self) -> bool:
        if self.schoolname and self.token:
            return True
        return False

    def save(self):
        data = {"schoolname": self.schoolname, "token": {self.token}}
        self.file.save(data)

    def setschoolname(self, schoolname: str):
        self.schoolname = schoolname
        self.save()

    def settoken(self, token):
        self.token = token
        self.save()
