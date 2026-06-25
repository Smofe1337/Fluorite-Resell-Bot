import logging
from bot.database.repository.users import UserRepository
from bot.core.exceptions import UserAlreadyExists

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, user_repo: UserRepository):
        self._user_repo = user_repo

    async def register_user(
        self,
        user_id: int,
        lang: str,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
    ):
        return await self._user_repo.add_user(
            user_id=user_id, lang=lang,
            username=username, first_name=first_name, last_name=last_name,
        )

    async def update_profile(
        self,
        user_id: int,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        lang: str | None = None,
    ):
        await self._user_repo.update_profile(user_id, username, first_name, last_name, lang)

    async def get_user(self, user_id: int):
        return await self._user_repo.get_user(user_id)

    async def get_user_info(self, user_id: int):
        return await self._user_repo.get_user_info(user_id)

    async def is_banned(self, user_id: int) -> bool:
        return await self._user_repo.is_banned(user_id)

    async def is_admin(self, user_id: int):
        return await self._user_repo.is_admin(user_id)

    async def get_all(self):
        return await self._user_repo.get_all()

    async def handle_order(self, user_id: int, sum: float, invite_link: str | None = None):
        await self._user_repo.increment_user(user_id, sum, invite_link=invite_link)

    async def update_balance(self, user_id: int, amount: float, operator: str):
        await self._user_repo.update_balance(user_id, amount, operator)

    async def set_user_ban_status(self, user_id: int, status: bool):
        await self._user_repo.set_user_ban_status(user_id, status)

    async def get_user_by_invite_link(self, invite_link: str):
        return await self._user_repo.get_user_by_invite_link(invite_link)

    async def get_balance(self, user_id: int):
        return await self._user_repo.get_balance(user_id)

    async def get_referral_count(self, user_id: int):
        return await self._user_repo.get_referral_count(user_id)

    async def on_new_referral(
            self,
            inviter_user_id: int,
            referral_user_id: int,
            amount_to_balance: int = 0,
    ):
        if await self._user_repo.is_user_exists(referral_user_id):
            raise UserAlreadyExists()

        await self._user_repo.add_new_referral(inviter_user_id, referral_user_id)
        await self._user_repo.update_referral_count(inviter_user_id)

        if amount_to_balance > 0:
            await self._user_repo.update_balance(inviter_user_id, amount_to_balance, '+')

    async def get_lang(self, user_id: int) -> str:
        user = await self.get_user(user_id)
        return user.lang

    async def bind_invite_link(self, user_id: int, invite_link: str):
        await self._user_repo.bind_invite_link(user_id, invite_link)

    async def is_vip(self, user_id: int) -> bool:
        user = await self._user_repo.get_user(user_id)
        return user.is_vip

    async def change_vip_status(self, user_id: int, is_vip: bool) -> None:
        await self._user_repo.change_vip_status(user_id, is_vip)

    async def delete_user(self, user_id: int) -> None:
        await self._user_repo.delete_user(user_id)

    async def delete_users_batch(self, user_ids: list[int]) -> None:
        await self._user_repo.delete_users_batch(user_ids)

    async def decrement_referral_count(self, inviter_id: int, count: int) -> None:
        await self._user_repo.decrement_referral_count(inviter_id, count)
