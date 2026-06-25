import logging
from sqlalchemy import select, and_, update, or_, delete
from bot.database.models.keys import Keys
from bot.database.repository.base import BaseRepository
from bot.core.exceptions import KeyAlreadyReceived, KeyTokenNotFound, KeyNotFound
from bot.enums.keys import KeyStatus

logger = logging.getLogger(__name__)


class KeysRepository(BaseRepository):

    async def add_new_key(self, keys: list[str], game_name: str, duration: int):
        async with self._session() as session:
            new_keys = []
            for key in keys:
                if await self.is_key_exists(key):
                    continue

                new_key = Keys(key=key, game_name=game_name, duration=duration)
                session.add(new_key)
                new_keys.append(new_key)

            await session.commit()
            return [k.orm_to_dict() for k in new_keys]

    async def is_key_exists(self, key: str) -> bool:
        async with self._session() as session:
            result = await session.execute(select(Keys).where(Keys.key == key))
            return result.scalars().first() is not None

    async def find_key(self, game_name: str, duration: int) -> Keys:
        async with self._session() as session:
            result = await session.execute(select(Keys).where(and_(
                Keys.game_name == game_name,
                Keys.duration == duration,
                Keys.status == KeyStatus.AVAILABLE.value
            )).limit(1))
            return result.scalars().first()

    async def has_available_keys(self, game_name: str) -> bool:
        async with self._session() as session:
            result = await session.execute(select(Keys).where(and_(
                Keys.game_name == game_name,
                Keys.status == KeyStatus.AVAILABLE.value
            )).limit(1))
            return result.scalars().first() is not None

    async def has_available_duration(self, game_name: str) -> dict:
        durations = [1, 7, 30]
        result = {'1d': False, '7d': False, '30d': False}

        async with self._session() as session:
            for days in durations:
                query = select(Keys).where(and_(
                    Keys.game_name == game_name,
                    Keys.duration == days,
                    Keys.status == KeyStatus.AVAILABLE.value
                )).limit(1)

                res = await session.execute(query)
                if res.scalars().first():
                    result[f'{days}d'] = True

        return result

    async def update_key(self, key: str, status: str, token: str | None = None):
        async with self._session() as session:
            values = {'status': status}
            if token is not None:
                values['token'] = token
            await session.execute(update(Keys).where(Keys.key == key).values(**values))
            await session.commit()

    async def get_key_by_token(self, token: str) -> Keys:
        async with self._session() as session:
            result = await session.execute(select(Keys).where(Keys.token == token))
            key_obj = result.scalars().first()
            if key_obj is None:
                raise KeyTokenNotFound()

            if key_obj.status == KeyStatus.RECEIVED.value:
                raise KeyAlreadyReceived()

            return key_obj

    async def bind_key_to_user(self, user_id: int, key: str):
        async with self._session() as session:
            await session.execute(update(Keys).where(Keys.key == key).values(owner_id=user_id))
            await session.commit()

    async def get_all_user_keys(self, user_id: int) -> list[str]:
        async with self._session() as session:
            result = await session.execute(select(Keys).where(and_(
                Keys.owner_id == user_id,
                or_(
                    Keys.status == KeyStatus.SOLD.value,
                    Keys.status == KeyStatus.RECEIVED.value
                )
            )))
            return [key.key for key in result.scalars().all()]

    async def get_all_keys(self) -> list:
        async with self._session() as session:
            result = await session.execute(select(Keys))
            return [
                {
                    'id': key.id,
                    'owner_id': key.owner_id,
                    'key': key.key,
                    'game': key.game_name,
                    'duration': key.duration,
                    'token': key.token,
                    'status': key.status,
                }
                for key in result.scalars().all()
            ]

    async def delete_key(self, key: str):
        if not await self.is_key_exists(key):
            raise KeyNotFound()

        async with self._session() as session:
            await session.execute(delete(Keys).where(Keys.key == key))
            await session.commit()

    async def rebind_game(self, current_game: str, new_name: str):
        async with self._session() as session:
            await session.execute(update(Keys).where(
                Keys.game_name == current_game
            ).values(game_name=new_name))
            await session.commit()

    async def delete_keys_by_game(self, game_name: str):
        async with self._session() as session:
            await session.execute(delete(Keys).where(and_(
                Keys.game_name == game_name,
                Keys.owner_id.is_(None)
            )))
            await session.commit()
