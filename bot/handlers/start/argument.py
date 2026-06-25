from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from bot.handlers.referral_system import ReferralHandler
from bot.handlers.gift import GiftHandler
from bot.handlers.callbacks.process_game import ProcessGames
from bot.database.service.users import UserService
from bot.core.exceptions import UserNotFound


class StartArgumentHandler:
    def __init__(self, user_service: UserService, process_games: ProcessGames,
                 referral_handler: ReferralHandler, gift_handler: GiftHandler):
        self._user_service = user_service
        self._process_games = process_games
        self._referral_handler = referral_handler
        self._gift_handler = gift_handler

    async def handle_argument(self, message: Message, func: str, data: str, state: FSMContext = None):
        user_id = message.from_user.id
        lang = message.from_user.language_code

        if func == 'ref':
            await self._referral_handler.handle_referral(message, data, state)
            return

        tg_user = message.from_user
        try:
            user_info = await self._user_service.get_user_info(user_id)
            await self._user_service.update_profile(
                user_id,
                username=tg_user.username,
                first_name=tg_user.first_name,
                last_name=tg_user.last_name,
                lang=lang,
            )
        except UserNotFound:
            await self._user_service.register_user(
                user_id, lang,
                username=tg_user.username,
                first_name=tg_user.first_name,
                last_name=tg_user.last_name,
            )
            user_info = await self._user_service.get_user_info(user_id)

        if user_info['is_banned']:
            return

        if func == 'gift':
            await self._gift_handler.handle_gift(message, data)

        elif func == 'game':
            await self._process_games.select_duration(message, data, lang)
