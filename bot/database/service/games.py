import logging
from bot.database.repository.games import GamesRepository
from bot.database.service.keys import KeysService
from bot.api.games.schemes import CreateGame, UpdateImage, UpdateGame
from bot.core.exceptions import GameNotFound
from typing import Dict

logger = logging.getLogger(__name__)


class GameService:
    def __init__(self, game_repo: GamesRepository, keys_service: KeysService):
        self._game_repo = game_repo
        self._keys_service = keys_service

    async def create_game(self, data: CreateGame):
        return await self._game_repo.add_new_game(
            data.game_name, data.pricing.day,
            data.pricing.week, data.pricing.month,
            data.image_url, data.status,
            data.is_need_show_img,
        )

    async def update_status(self, game_name: str, status: str):
        await self._game_repo.update_status(game_name, status)

    async def update_image(self, data: UpdateImage):
        await self._game_repo.update_image(data.game_name, data.image_url)

    async def get_game(self, game_name: str):
        return await self._game_repo.get_game(game_name)

    async def get_games(self):
        return await self._game_repo.get_games()

    async def get_game_price(
            self,
            game_name: str,
            target_currency: str,
            exchange_rates: dict,
    ) -> Dict[str, Dict[str, int]]:
        return await self._game_repo.get_game_prices(game_name, target_currency, exchange_rates)

    async def get_all_games(self):
        return await self._game_repo.get_all_games()

    async def on_delete(self, game_name: str):
        if not await self._game_repo.is_game_exists(game_name):
            raise GameNotFound()

        await self._game_repo.delete(game_name)
        await self._keys_service._keys_repo.delete_keys_by_game(game_name)

    async def on_update(self, data: UpdateGame):
        await self._game_repo.update_game(
            data.updating_game, data.name,
            data.pricing, data.image_url, data.status,
        )

        if data.updating_game != data.name:
            await self._keys_service.rebind_game(data.updating_game, data.name)

    async def update_visibility(self, game_name: str, status: bool):
        await self._game_repo.update_visibility(game_name, status)
