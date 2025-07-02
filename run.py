from zermelo_api import loadAPI
import asyncio
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(filename="example.log", encoding="utf-8", level=logging.DEBUG)

SCHOOLNAME = "carmelhengelo"
CODE = "012 345 678 910"


async def main():
    api = await loadAPI(SCHOOLNAME)
    logger.debug(api.loaded)
    try:
        await api.login(CODE)
    except Exception as e:
        logger.exception(e)

asyncio.run(main())
