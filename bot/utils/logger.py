from aiogram import Bot
from config import Config

class Logger:
    def __init__(self, bot: Bot):
        self.bot = bot
    

    async def send_log(self, user_id: int, info: str, **kwargs) -> None:
        unpaked = ''.join(f'{k} -> {v}' for k, v, in kwargs.items())
        message = f'{info}\nUser -> tg://user?id={user_id}\nDetail:\n{unpaked}'
        await self.bot.send_message(chat_id=Config.OWNER_ID, text=message)


    @staticmethod
    async def write_to_file(user_id: int, **kwargs) -> None:
        pass
