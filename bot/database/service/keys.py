import logging
from bot.database.repository.keys import KeysRepository
from bot.database.repository.games import GamesRepository
from bot.enums.keys import KeyStatus
from bot.api.keys.schemes import NewKey
from bot.core.exceptions import GameNotFound

logger = logging.getLogger(__name__)


class KeysService:
    def __init__(self, keys_repo: KeysRepository, game_repo: GamesRepository):
        self._keys_repo = keys_repo
        self._game_repo = game_repo

    async def on_new_key(self, data: NewKey):
        if not await self._game_repo.is_game_exists(data.game_name):
            raise GameNotFound()
        return await self._keys_repo.add_new_key(data.keys, data.game_name, data.duration)

    async def get_key(self, game_name: str, duration: int):
        return await self._keys_repo.find_key(game_name, duration)

    async def get_key_by_token(self, token: str):
        key = await self._keys_repo.get_key_by_token(token)
        if key:
            await self.update_key(key.key, KeyStatus.RECEIVED.value)
            return key

    async def has_keys(self, game_name: str) -> bool:
        return await self._keys_repo.has_available_keys(game_name)

    async def has_duration(self, game_name: str) -> dict:
        return await self._keys_repo.has_available_duration(game_name)

    async def update_key(self, key: str, status: str, token: str | None = None):
        await self._keys_repo.update_key(key, status, token)

    async def bind_key_to_user(self, user_id: int, key: str):
        await self._keys_repo.bind_key_to_user(user_id, key)

    async def get_all_keys_by_user(self, user_id: int):
        return await self._keys_repo.get_all_user_keys(user_id)

    async def get_all_keys(self):
        return await self._keys_repo.get_all_keys()

    async def delete_key(self, key: str):
        await self._keys_repo.delete_key(key)

    async def rebind_game(self, current_name: str, new_name: str):
        await self._keys_repo.rebind_game(current_name, new_name)
