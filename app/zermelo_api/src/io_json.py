import aiohttp


async def get_json(url: str):
    async with aiohttp.ClientSession() as client:
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
