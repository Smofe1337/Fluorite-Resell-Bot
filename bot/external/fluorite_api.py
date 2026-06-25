from typing import List
from config import Config
import aiohttp
import asyncio
import sys


class FluoriteApi:
    def __init__(self):
        self.token = Config.FLUORITE_API_TOKEN
        self.headers = {
            'X-API-Key': Config.FLUORITE_API_TOKEN
        }
        
        if not self.token or self.token is None:
            print('[FluoriteAPI] API KEY IS REQUIRED')
            sys.exit(1)    
    

    async def ban_keys(self, keys: List[str]) -> bool:
        async with aiohttp.ClientSession() as session:
            for key in keys:
                json = {'key': key, 'duration': 863913600, 'reason': 'fuck u'}
                async with session.post(
                    url=Config.BASE_URL_FL + 'ban',
                    headers=self.headers,
                    json=json
                ) as response:
                    data = await response.json()

                    if data['status'] != 'success':
                        return False
                
                await asyncio.sleep(0.3)  # To avoid hitting rate limits
            
            return True

    
    async def reset_hwid(self, key: str) -> bool:
        json = {
            'key': key
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=Config.BASE_URL_FL + 'reset',
                headers=self.headers,
                json=json
            ) as response:
                data = await response.json()

                if data['status'] == 'success':
                    return True
                
            return False
