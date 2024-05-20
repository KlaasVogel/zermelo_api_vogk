from zermelo_api import Branches, loadAPI


async def main():
    zermelo = loadAPI("carmelhengelo")
    branches = Branches(zermelo)
    await Branches._init("")
    for branch in branches:
        print(branch)
    #     if branch.branch == "lg":
    #         branch.load_lesgroepen()
