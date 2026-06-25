from bot.database.db import engine
from bot.database.base import Base
from bot.database.models.users import Users


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
