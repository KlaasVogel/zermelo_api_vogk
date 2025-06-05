from zermelo_api import load_schools
import asyncio
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(filename="example.log", encoding="utf-8", level=logging.DEBUG)

async def main():
    schoolyears, branches = await load_schools("carmelhengelo")
    branch = branches.get("lg")
    print(branch)
    print(schoolyears)
    [logger.debug(vak) for vak in branch.vakken]

asyncio.run(main())
