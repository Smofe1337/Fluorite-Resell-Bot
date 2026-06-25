import logging
from time import time
from bot.database.repository.channel_guard import ChannelGuardRepository

logger = logging.getLogger(__name__)


class ChannelGuardService:
    def __init__(self, repo: ChannelGuardRepository) -> None:
        self._repo = repo

    async def log(self, user_id: int, score: int, action: str, reason: str, is_raid: bool) -> None:
        await self._repo.add_log(user_id, time(), score, action, reason, is_raid)

    async def get_recent_ts(self, since_ts: float) -> list[float]:
        return await self._repo.get_recent_ts(since_ts)

    async def get_stats(self) -> dict:
        return await self._repo.get_stats()
