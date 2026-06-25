from fastapi import APIRouter, Depends
from fastapi.responses import Response
from bot.api.dashboard.oauth2.security import get_current_user
from bot.core.error_handlers import hook_exceptions
from bot.localization.localizer import localize
from bot.utils.converters import convert_from_usd
from bot.utils.maps import get_currency_by_lang
from bot.api.users.schemes import UpdateBalance, SetBanStatus, SetVipStatus
from bot.database.service.users import UserService
from aiogram import Bot


class AvatarRouter:
    def __init__(self, bot: Bot):
        self._bot = bot
        self.router = APIRouter()
        self._register_routes()

    def _register_routes(self):
        self.router.get('/users/{user_id}/avatar/')(self._get_avatar)

    async def _get_avatar(self, user_id: int, token: str = ''):
        from jose import jwt, JWTError
        from config import Config
        try:
            jwt.decode(token, Config.SECRET, algorithms=['HS256'])
        except (JWTError, Exception):
            return Response(status_code=401)
        try:
            photos = await self._bot.get_user_profile_photos(user_id, limit=1)
            if not photos.photos:
                return Response(status_code=204)
            photo = photos.photos[0][-1]
            file = await self._bot.get_file(photo.file_id)
            from aiohttp import ClientSession
            url = f'https://api.telegram.org/file/bot{self._bot.token}/{file.file_path}'
            async with ClientSession() as session:
                async with session.get(url) as resp:
                    data = await resp.read()
                    content_type = resp.headers.get('Content-Type', 'image/jpeg')
            return Response(content=data, media_type=content_type, headers={'Cache-Control': 'public, max-age=3600'})
        except Exception:
            return Response(status_code=204)


class UsersRouter:
    def __init__(self, user_service: UserService, bot: Bot):
        self._user_service = user_service
        self._bot = bot
        self.router = APIRouter(dependencies=[Depends(get_current_user)])
        self._register_routes()

    def _register_routes(self):
        self.router.get('/users/')(self._get_users)
        self.router.get('/users/{user_id}/')(hook_exceptions(self._get_user))
        self.router.post('/users/update-balance/')(hook_exceptions(self._update_balance))
        self.router.post('/users/set-ban-status/')(hook_exceptions(self._set_ban_status))
        self.router.post('/users/set-vip-status/')(hook_exceptions(self._set_vip_status))

    async def _get_users(self):
        return await self._user_service.get_all()

    async def _get_user(self, user_id: int):
        user = await self._user_service.get_user(user_id)
        return {
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

    async def _update_balance(self, data: UpdateBalance):
        await self._user_service.update_balance(data.user_id, data.amount, data.operator)
        user_data = await self._user_service.get_user_info(data.user_id)

        lang = user_data['language']
        balance = user_data['balance']

        currence = get_currency_by_lang(lang)
        converted_balance = await convert_from_usd(currence, balance)

        await self._bot.send_message(
            chat_id=data.user_id,
            text=await localize(lang, 'balance_update_notification', round(converted_balance, 2))
        )

        return {
            'Status': True,
            'Message': 'Balance updated successfully'
        }

    async def _set_ban_status(self, data: SetBanStatus):
        await self._user_service.set_user_ban_status(data.user_id, data.status)
        status = 'banned' if data.status else 'unbanned'
        return {
            'Status': True,
            'Message': f'User {status} successfully'
        }

    async def _set_vip_status(self, data: SetVipStatus):
        await self._user_service.change_vip_status(data.user_id, data.status)
        status = 'granted' if data.status else 'revoked'
        return {
            'Status': True,
            'Message': f'VIP {status} successfully'
        }
