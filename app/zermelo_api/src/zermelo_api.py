from __future__ import annotations
from .credentials import Credentials
import inspect
import logging
import asyncio
import aiohttp
import json
from dataclasses import dataclass

logger = logging.getLogger(__name__)


async def get_json(client: aiohttp.ClientSession, url: str):
    async with client.get(url) as response:
        assert response.status == 200
        return await response.read()


async def post_request(url: str, data: dict):
    async with aiohttp.ClientSession() as session:
        response = await session.post(
            url="https://httpbin.org/post",
            data={"key": "value"},
            headers={"Content-Type": "application/json"},
        )
        return await response.json()


async def loadAPI(name: str) -> ZermeloAPI:
    zermelo = ZermeloAPI(name)
    if not await zermelo.checkCreds():
        with open("creds.ini") as f:
            token = f.read()
            await zermelo.add_token(token)
    return zermelo


class ZermeloAPI:

    def __init__(self, school: str):
        self.credentials = Credentials()
        self.zerurl = f"https://{school}.zportal.nl/api/v3/"

    def login(self, code: str) -> bool:
        token = self.get_access_token(code)
        return self.add_token(token)

    async def get_access_token(self, code: str) -> str:
        token = ""
        url = self.zerurl + "oauth/token"
        data = {"grant_type": "authorization_code", "code": code}
        response = await post_request(url, data)
        logger.debug(response)
        exit()

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

    async def checkCreds(self):
        try:
            self.getName()
            result = True
        except Exception as e:
            logger.error(e)
            result = False
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

    async def getData(self, task, from_id=False) -> list[dict] | str:
        request = (
            self.zerurl + task + f"?access_token={self.credentials.token}"
            if from_id
            else self.zerurl + task + f"&access_token={self.credentials.token}"
        )
        logger.debug(request)
        async with aiohttp.ClientSession() as client:
            data1 = await get_json(client, request)
            jn = json.loads(data1.decode("utf-8"))
            logger.info(f"json: {jn}")

        #     json_response = requests.get(request).json()
        #     if json_response:
        #         json_status = json_response["response"]["status"]
        #         if json_status == 200:
        #             result = (200, json_response["response"]["data"])
        #             logger.debug("    **** JSON OK ****")
        #         else:
        #             logger.debug(
        #                 f"oeps, geen juiste response: {task} - {json_response['response']}"
        #             )
        #             result = (json_status, json_response["response"])
        #     else:
        #         logger.error("JSON - response is leeg")
        # except Exception as e:
        #     logger.error(e)
        # finally:
        #     return result

    async def load_query(self, query: str) -> list[dict]:
        try:
            status, data = await self.getData(query)
            if status != 200:
                raise Exception(f"Error loading data {status}")
            if not data:
                logger.debug("no data")
        except Exception as e:
            logger.debug(e)
            data = []
        return data


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


@dataclass
class ZermeloCollection(list):
    zermelo: ZermeloAPI

    async def load_collection(self, query: str, type: object, *args, **kwargs) -> None:
        data = await self.zermelo.load_query(query)
        for row in data:
            self.append(from_zermelo_dict(type, row, *args, **kwargs))

    # def test(self, query: str):
    #     data = self.zermelo.load_query(query)
    #     for row in data:
    #         logger.info(f"test: {row}")
