import logging
from bot.database.repository.dashboard.staff import StaffRepository
from bot.api.dashboard.schemes import Auth

logger = logging.getLogger(__name__)


class StaffService:
    def __init__(self, staff_repo: StaffRepository):
        self._staff_repo = staff_repo

    async def on_auth(self, data: Auth) -> bool:
        return await self._staff_repo.auth_user(data.username, data.password)

    async def create_user(self, username: str, password: str):
        await self._staff_repo.create(username, password)

    async def delete_user(self, username: str):
        await self._staff_repo.delete(username)

    async def get_user(self, username: str):
        return await self._staff_repo.get_user(username)
