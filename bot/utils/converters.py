from async_lru import alru_cache
import aiohttp


@alru_cache(maxsize=1, ttl=1500)
async def get_usd_price() -> dict:
    url = 'https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/usd.json'

    async with aiohttp.ClientSession() as session:
        async with session.get(url=url) as resp:
            json_obj = await resp.json()
            return json_obj['usd']
        

@alru_cache(maxsize=1, ttl=1500)
async def get_ruble_price():
    url = 'https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/rub.json'

    async with aiohttp.ClientSession() as session:
        async with session.get(url=url) as resp:
            json_obj = await resp.json()
            return json_obj['rub']['usd']
        

@alru_cache(maxsize=1, ttl=1500)
async def ruble_to_usd(rub_amount: float) -> float:
    url = 'https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/rub.json'

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            json_obj = await resp.json()
            return json_obj['rub']['usd'] * rub_amount


@alru_cache(maxsize=1, ttl=1500)
async def convertor(currency: str, amount: float) -> float:
    if currency == 'usd':
        return amount
    
    url = f'https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/{currency}.json'

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            json_obj = await resp.json()
            return json_obj[currency]['usd'] * amount


@alru_cache(maxsize=1, ttl=1500)
async def convert_from_usd(currency: str, amount: float) -> float:
    if currency == 'usd':
        return amount
    
    url = 'https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/usd.json'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            json_obj = await resp.json()
            return json_obj['usd'][currency] * amount
    