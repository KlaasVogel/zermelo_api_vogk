from .config import getConfig
from .logger import makeLogger, INFO, DEBUG

logger = makeLogger("creds", INFO)


class Credentials:
    def __init__(self):
        self.file = getConfig("creds")
        print(self.file)
        self.token = ""
        self.load()

    def load(self):
        self.token = ""
        try:
            data = self.file.load()
            self.token = data["token"]
        except Exception as e:
            logger.trace()
        finally:
            logger.debug(f"token: {self.token}")
            return True if self.token else False

    def settoken(self, token):
        self.file.save({"token": token})
        self.token = token
