import aiohttp
import asyncio
import time
from logger import log_info, log_error
from config import API_LIST
from db import insert_metric

async def check_single_api(session, url):
    try:
        start = time.time()
        async with session.get(url, timeout=5) as response:
            latency = round((time.time() - start) * 1000, 2)

            if response.status == 200:
                log_info(f"{url} UP | {latency} ms")
                insert_metric(url, "UP", latency)
                return (url, "UP", latency)
            else:
                log_error(f"{url} ERROR {response.status}")
                insert_metric(url, "ERROR", 0)
                return (url, "ERROR", 0)

    except Exception as e:
        log_error(f"{url} DOWN | {str(e)}")
        insert_metric(url, "DOWN", 0)
        return (url, "DOWN", 0)

async def check_apis_async():
    async with aiohttp.ClientSession() as session:
        tasks = [check_single_api(session, url) for url in API_LIST]
        return await asyncio.gather(*tasks)