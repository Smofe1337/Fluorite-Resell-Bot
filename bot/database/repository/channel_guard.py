import logging
from sqlalchemy import select, func
from bot.database.models.channel_guard import ChannelGuardLog
from bot.database.repository.base import BaseRepository

logger = logging.getLogger(__name__)


class ChannelGuardRepository(BaseRepository):

    async def add_log(
        self,
        user_id: int,
        ts: float,
        score: int,
        action: str,
        reason: str,
        is_raid: bool,
    ) -> None:
        async with self._session() as session:
            session.add(ChannelGuardLog(
                user_id=user_id,
                ts=ts,
                score=score,
                action=action,
                reason=reason,
                is_raid=is_raid,
            ))
            await session.commit()

    async def get_recent_ts(self, since_ts: float) -> list[float]:
        async with self._session() as session:
            result = await session.execute(
                select(ChannelGuardLog.ts).where(ChannelGuardLog.ts >= since_ts)
            )
            return [row[0] for row in result.all()]

    async def get_stats(self) -> dict:
        async with self._session() as session:
            total = await session.execute(select(func.count()).select_from(ChannelGuardLog))
            banned = await session.execute(
                select(func.count()).select_from(ChannelGuardLog).where(ChannelGuardLog.action == 'ban')
            )
            raids = await session.execute(
                select(func.count()).select_from(ChannelGuardLog).where(ChannelGuardLog.is_raid.is_(True))
            )
            return {
                'total_joins': total.scalar() or 0,
                'banned': banned.scalar() or 0,
                'raid_events': raids.scalar() or 0,
            }
