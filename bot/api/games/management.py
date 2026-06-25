from fastapi import APIRouter, Depends
from bot.api.games.schemes import (
    CreateGame,
    UpdateStatus,
    UpdateImage,
    Delete,
    UpdateGame,
    UpdateGameVisibility
)
from bot.api.dashboard.oauth2.security import get_current_user
from bot.enums.games import GameStatus
from bot.core.error_handlers import hook_exceptions
from bot.database.service.games import GameService
from config import Config


class GamesRouter:
    def __init__(self, game_service: GameService):
        self._game_service = game_service
        self.router = APIRouter(dependencies=[Depends(get_current_user)])
        self._register_routes()

    def _register_routes(self):
        self.router.get('/games/')(self._get_games)
        self.router.post('/games/create/')(hook_exceptions(self._create_game))
        self.router.post('/games/update-status/')(hook_exceptions(self._update_status))
        self.router.post('/games/update-image/')(hook_exceptions(self._update_image))
        self.router.post('/games/delete/')(hook_exceptions(self._delete_game))
        self.router.post('/game/update/')(hook_exceptions(self._update_game))
        self.router.post('/game/update-visibility/')(hook_exceptions(self._update_visibility))

    async def _get_games(self):
        default_url = f'{Config.API_BASE_URL}/api/static/images/{Config.DEFAULT_GAME_IMAGE}'
        games = await self._game_service.get_all_games()
        for game in games:
            if not game.get('screenshot') or not game['screenshot'].startswith(Config.API_BASE_URL):
                game['screenshot'] = default_url
        return games

    async def _create_game(self, data: CreateGame):
        if not data.image_url:
            data.image_url = f'{Config.API_BASE_URL}/api/static/images/{Config.DEFAULT_GAME_IMAGE}'
        new_game = await self._game_service.create_game(data)
        return {
            'Status': True,
            'Message': 'Game successfully created',
            'Game': new_game
        }

    async def _update_status(self, data: UpdateStatus):
        available_status = [status.value for status in GameStatus]
        capitalize_status = data.new_status.capitalize()

        if capitalize_status not in available_status:
            return {
                'Status': False,
                'Error': 'Invalid status',
                'Message': f'Available status: {available_status}'
            }

        await self._game_service.update_status(data.game_name, capitalize_status)
        return {
            'Status': True,
            'Message': 'Status updated successfully'
        }

    async def _update_image(self, data: UpdateImage):
        await self._game_service.update_image(data)
        return {
            'Status': True,
            'Message': 'Image updated successfully'
        }

    async def _delete_game(self, data: Delete):
        await self._game_service.on_delete(data.game_name)

    async def _update_game(self, data: UpdateGame):
        await self._game_service.on_update(data)

    async def _update_visibility(self, data: UpdateGameVisibility):
        await self._game_service.update_visibility(data.updating_game, data.status)
        return {
            'Status': True,
            'Message': 'Game visibility updated successfully'
        }
