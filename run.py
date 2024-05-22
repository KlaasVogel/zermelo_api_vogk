from zermelo_api import Branches, loadAPI
import asyncio
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(filename="example.log", encoding="utf-8", level=logging.DEBUG)

async def main():
    zermelo = await loadAPI("carmelhengelo")
    branches = Branches(zermelo)
    await branches._init("")
    for branch in branches:
        if branch.branch == "lg":
            lesgroepen = await branch.find_lesgroepen()

asyncio.run(main())
