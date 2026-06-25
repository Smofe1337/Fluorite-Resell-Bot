import logging
from sqlalchemy import select, delete
from bot.database.repository.base import BaseRepository
from bot.database.models.dashboard.staff import Staff
from bot.core.exceptions import UserNotFound, InvalidPassword, UserAlreadyExists
from bot.core.security import PasswordManager

logger = logging.getLogger(__name__)


class StaffRepository(BaseRepository):
    def __init__(self, password_manager: PasswordManager):
        self._password_manager = password_manager

    async def create(self, username: str, password: str):
        if await self.is_user_exists(username):
            raise UserAlreadyExists()

        async with self._session() as session:
            hashed_password = self._password_manager.password_to_hash(password)
            new_user = Staff(username=username, password=hashed_password)
            session.add(new_user)
            await session.commit()

    async def is_user_exists(self, username: str):
        async with self._session() as session:
            result = await session.execute(select(Staff).where(Staff.username == username))
            return result.scalar_one_or_none()

    async def auth_user(self, username: str, password: str) -> bool:
        if await self.is_user_exists(username) is None:
            raise UserNotFound()

        user = await self.get_user(username)
        if not self._password_manager.verif(password, user.password):
            raise InvalidPassword()

        return True

    async def get_user(self, username: str) -> Staff | None:
        async with self._session() as session:
            result = await session.execute(select(Staff).where(Staff.username == username))
            return result.scalar_one_or_none()

    async def delete(self, username: str):
        if await self.is_user_exists(username) is None:
            raise UserNotFound()

        async with self._session() as session:
            await session.execute(delete(Staff).where(Staff.username == username))
            await session.commit()

    async def get_all_users(self) -> list:
        async with self._session() as session:
            result = await session.execute(select(Staff))
            return [
                Staff.orm_to_dict(user, exclude=['password'])
                for user in result.scalars().all()
            ]
