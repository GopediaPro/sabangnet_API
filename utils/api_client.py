import aiohttp

async def aiohttp_post(url, json, timeout=30, logger=None):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                json=json,
                headers={"Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as response:
                data = await response.json()
                if response.status != 200:
                    if logger:
                        logger.error(f"API POST {url} failed: HTTP {response.status}, {data}")
                    return None, response.status, data
                return data, response.status, None
    except Exception as e:
        if logger:
            logger.error(f"API POST {url} exception: {e}")
        return None, None, str(e) 