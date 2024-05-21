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
        logger.info(branch)
    #     if branch.branch == "lg":
    #         branch.load_lesgroepen()

asyncio.run(main())
