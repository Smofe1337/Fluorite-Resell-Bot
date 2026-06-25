import logging
from sqlalchemy import select, update, delete
from bot.database.models.users import Users, Referrals
from bot.database.repository.base import BaseRepository
from bot.core.exceptions import UserNotFound, InvalidOperator

logger = logging.getLogger(__name__)


class UserRepository(BaseRepository):

    async def add_user(
        self,
        user_id: int,
        lang: str,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
    ):
        if await self.is_user_exists(user_id):
            raise UserNotFound()

        async with self._session() as session:
            new_user = Users(
                user_id=user_id,
                lang=lang,
                username=username,
                first_name=first_name,
                last_name=last_name,
            )
            session.add(new_user)
            await session.commit()

    async def update_profile(
        self,
        user_id: int,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        lang: str | None = None,
    ):
        async with self._session() as session:
            values = {}
            if username is not None:
                values['username'] = username
            if first_name is not None:
                values['first_name'] = first_name
            if last_name is not None:
                values['last_name'] = last_name
            if lang is not None:
                values['lang'] = lang
            if values:
                await session.execute(
                    update(Users).where(Users.user_id == user_id).values(**values)
                )
                await session.commit()

    async def is_user_exists(self, user_id: int) -> bool:
        async with self._session() as session:
            result = await session.execute(select(Users).where(Users.user_id == user_id))
            return result.scalar_one_or_none() is not None

    async def is_banned(self, user_id: int) -> bool:
        if not await self.is_user_exists(user_id):
            raise UserNotFound()

        async with self._session() as session:
            result = await session.execute(select(Users).where(Users.user_id == user_id))
            user = result.scalars().first()
            return user.is_banned

    async def get_user(self, user_id: int) -> Users:
        if not await self.is_user_exists(user_id):
            raise UserNotFound()

        async with self._session() as session:
            result = await session.execute(select(Users).where(Users.user_id == user_id))
            return result.scalars().first()

    async def get_user_info(self, user_id: int) -> dict:
        if not await self.is_user_exists(user_id):
            raise UserNotFound()

        async with self._session() as session:
            result = await session.execute(select(Users).where(Users.user_id == user_id))
            user = result.scalars().first()

            available_langs = ['ru', 'en']
            lang = user.lang if user.lang in available_langs else 'en'

            return {
                'is_banned': user.is_banned,
                'is_admin': user.is_admin,
                'balance': user.balance,
                'language': lang,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
            }

    async def increment_user(self, user_id: int, sum: float, invite_link: str | None = None):
        if not await self.is_user_exists(user_id):
            raise UserNotFound()

        async with self._session() as session:
            result = await session.execute(select(Users).where(Users.user_id == user_id))
            user = result.scalars().first()

            user.total_order += 1
            user.total_spent += sum
            user.invite_link = invite_link

            if not user.is_vip:
                user.is_vip = True

            await session.commit()

    async def update_balance(self, user_id: int, amount: float, operator: str):
        if not await self.is_user_exists(user_id):
            raise UserNotFound()

        async with self._session() as session:
            result = await session.execute(select(Users).where(Users.user_id == user_id))
            user = result.scalars().first()

            if operator == '+':
                user.balance += amount
            elif operator == '-':
                user.balance -= amount
                if user.balance < 0:
                    user.balance = 0
            else:
                raise InvalidOperator()

            await session.commit()

    async def get_all(self) -> list:
        async with self._session() as session:
            result = await session.execute(select(Users))
            users = result.scalars().all()

            return [
                {
                    'id': user.id,
                    'user_id': user.user_id,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'lang': user.lang,
                    'register_at': user.register_at,
                    'balance': user.balance,
                    'total_order': user.total_order,
                    'total_spent': user.total_spent,
                    'total_invited': user.total_invited,
                    'is_admin': user.is_admin,
                    'is_banned': user.is_banned,
                    'is_vip': user.is_vip,
                }
                for user in users
            ]

    async def set_user_ban_status(self, user_id: int, ban: bool):
        if not await self.is_user_exists(user_id):
            raise UserNotFound()

        async with self._session() as session:
            await session.execute(update(Users).where(Users.user_id == user_id).values(is_banned=ban))
            await session.commit()

    async def is_admin(self, user_id: int):
        if not await self.is_user_exists(user_id):
            raise UserNotFound()

        async with self._session() as session:
            result = await session.execute(select(Users).where(Users.user_id == user_id))
            return result.scalars().first().is_admin

    async def get_user_by_invite_link(self, invite_link: str) -> Users:
        async with self._session() as session:
            result = await session.execute(select(Users).where(Users.invite_link == invite_link))
            return result.scalars().first()

    async def bind_invite_link(self, user_id: int, invite_link: str):
        if not await self.is_user_exists(user_id):
            raise UserNotFound()

        async with self._session() as session:
            await session.execute(update(Users).where(Users.user_id == user_id).values(invite_link=invite_link))
            await session.commit()

    async def get_balance(self, user_id: int):
        if not await self.is_user_exists(user_id):
            raise UserNotFound()

        async with self._session() as session:
            result = await session.execute(select(Users).where(Users.user_id == user_id))
            return result.scalars().first().balance

    async def get_referral_count(self, user_id: int) -> int:
        if not await self.is_user_exists(user_id):
            raise UserNotFound()

        async with self._session() as session:
            result = await session.execute(select(Users).where(Users.user_id == user_id))
            return result.scalars().first().total_invited

    async def update_referral_count(self, user_id: int):
        async with self._session() as session:
            await session.execute(
                update(Users)
                .where(Users.user_id == user_id)
                .values(total_invited=Users.total_invited + 1)
            )
            await session.commit()

    async def add_new_referral(self, inviter_user_id: int, referral_user_id: int):
        async with self._session() as session:
            new_referral = Referrals(
                inviter_user_id=inviter_user_id, referral_user_id=referral_user_id
            )
            session.add(new_referral)
            await session.commit()

    async def get_lang(self, user_id: int) -> str:
        if not await self.is_user_exists(user_id):
            raise UserNotFound()

        async with self._session() as session:
            result = await session.execute(select(Users).where(Users.user_id == user_id))
            return result.scalars().first().lang

    async def change_vip_status(self, user_id: int, is_vip: bool) -> None:
        async with self._session() as session:
            await session.execute(update(Users).where(Users.user_id == user_id).values(is_vip=is_vip))
            await session.commit()

    async def delete_user(self, user_id: int) -> None:
        async with self._session() as session:
            await session.execute(delete(Referrals).where(Referrals.referral_user_id == user_id))
            await session.execute(delete(Users).where(Users.user_id == user_id))
            await session.commit()

    async def delete_users_batch(self, user_ids: list[int]) -> None:
        if not user_ids:
            return
        async with self._session() as session:
            await session.execute(delete(Referrals).where(Referrals.referral_user_id.in_(user_ids)))
            await session.execute(delete(Users).where(Users.user_id.in_(user_ids)))
            await session.commit()

    async def decrement_referral_count(self, inviter_id: int, count: int) -> None:
        async with self._session() as session:
            await session.execute(
                update(Users)
                .where(Users.user_id == inviter_id)
                .values(total_invited=Users.total_invited - count)
            )
            await session.commit()
