from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from bot.database.service.users import UserService
from bot.handlers.keyboard import KeyBoard
from bot.views.profile import send_user_profile
from bot.views.game_message import send_game_message


class TextRouter:
    def __init__(self, key_board: KeyBoard, user_service: UserService):
        self._key_board = key_board
        self._user_service = user_service
        self.router = Router()
        self._register_routes()

    def _register_routes(self):
        self.router.message(F.text.in_(['Каталог', 'Catalog']))(self._process_catalog)
        self.router.message(F.text.in_(['Подарить ключ', 'Gift key']))(self._process_gifts)
        self.router.message(F.text.in_(['Профиль', 'Profile']))(self._process_profile)

    async def _process_catalog(self, message: Message, state: FSMContext) -> None:
        if await self._user_service.is_banned(message.from_user.id):
            return
        await state.update_data({'is_gift': False})
        await send_game_message(message)

    async def _process_gifts(self, message: Message, state: FSMContext) -> None:
        if await self._user_service.is_banned(message.from_user.id):
            return
        await state.update_data({'is_gift': True})
        await send_game_message(message)

    async def _process_profile(self, message: Message) -> None:
        if await self._user_service.is_banned(message.from_user.id):
            return
        lang = message.from_user.language_code
        await message.answer(
            text=await send_user_profile(message),
            reply_markup=await self._key_board.get_profile(lang)
        )
