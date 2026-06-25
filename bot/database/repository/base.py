import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator
from sqlalchemy.ext.asyncio import AsyncSession
from bot.database.db import async_session_maker

logger = logging.getLogger(__name__)


class BaseRepository:
    @asynccontextmanager
    async def _session(self) -> AsyncIterator[AsyncSession]:
        async with async_session_maker() as session:
            yield session
