from zermelo_api import loadAPI
import asyncio
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(filename="example.log", encoding="utf-8", level=logging.DEBUG)


async def main(schoolname: str, code: str):
    api = await loadAPI(schoolname)
    try:
        await api.login(code)
        if api.checkCreds():
            print("")
    except Exception as e:
        logger.exception(e)


if __name__ == "__main__":
    print("updating credentials")
    schoolname = ""
    code = ""
    while not schoolname:
        schoolname = input("name of school:")

    while not code:
        code = input("code: ")

    asyncio.run(main(schoolname, code))
