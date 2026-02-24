import aiohttp
import asyncio
import time
from db import insert_metric


async def check_single_api(session, url):
    try:
        start = time.time()
        async with session.get(url, timeout=5) as response:
            latency = round((time.time() - start) * 1000, 2)

            if response.status == 200:
                insert_metric(url, "UP", latency)
                return (url, "UP", latency)
            else:
                insert_metric(url, "ERROR", latency)
                return (url, "ERROR", latency)

    except Exception:
        insert_metric(url, "DOWN", 0)
        return (url, "DOWN", 0)


async def check_apis_async(api_list):
    async with aiohttp.ClientSession() as session:
        tasks = [check_single_api(session, url) for url in api_list]
        return await asyncio.gather(*tasks)
