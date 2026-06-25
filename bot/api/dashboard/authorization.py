from fastapi import APIRouter, Response
from bot.api.dashboard.schemes import Auth, OAuth2
from bot.core.error_handlers import hook_exceptions
from bot.api.dashboard.oauth2.security import SecurityManager
from bot.database.service.dashboard.staff import StaffService


class AuthRouter:
    def __init__(self, staff_service: StaffService, security_manager: SecurityManager):
        self._staff_service = staff_service
        self._security_manager = security_manager
        self.router = APIRouter()
        self._register_routes()

    def _register_routes(self):
        self.router.post('/auth/')(hook_exceptions(self._authorization))
        self.router.post('/validate-token/')(hook_exceptions(self._validate_token))

    async def _authorization(self, data: Auth, response: Response):
        await self._staff_service.on_auth(data)
        access_token = SecurityManager.create_token({'username': data.username})
        return {
            'Status': True,
            'Message': 'Successfully authorized',
            'token': access_token
        }

    async def _validate_token(self, data: OAuth2):
        username = await self._security_manager.validate_token(data.token)
        if await self._staff_service._staff_repo.is_user_exists(username) is not None:
            return {
                'Status': True,
                'Message': 'Token is valid'
            }
