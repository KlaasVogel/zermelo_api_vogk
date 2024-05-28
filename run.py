from zermelo_api import load_branches
import asyncio
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(filename="example.log", encoding="utf-8", level=logging.DEBUG)

async def main():
    branches = await load_branches("carmelhengelo")
    branch = branches.get("lg")
    print(branch)
    data = await branch.get_vak_doc_loks()
    [logger.info(row) for row in data]
    # for branch in branches:
    #     if branch.branch == "lg":
    #         lesgroepen = await branch.find_lesgroepen()

asyncio.run(main())
