from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from bot.state.admins import CreateUser, DeleteUser
from bot.core.exceptions import UserAlreadyExists, UserNotFound
from bot.utils.generator import generate_password
from bot.core.permission import admin_only
from bot.database.service.dashboard.staff import StaffService
from bot.handlers.keyboard import KeyBoard


class DashboardFSMRouter:
    def __init__(self, staff_service: StaffService, key_board: KeyBoard):
        self._staff_service = staff_service
        self._key_board = key_board
        self.router = Router()
        self._register_routes()

    def _register_routes(self):
        self.router.message(CreateUser.input_username)(admin_only(self._create_user))
        self.router.message(DeleteUser.input_username)(admin_only(self._delete_user))

    async def _create_user(self, message: Message, state: FSMContext):
        username = message.text.strip()
        password = generate_password()

        try:
            await self._staff_service.create_user(username, password)
        except UserAlreadyExists:
            await message.answer(f'<b>User with username {username} already exists</b>')
            return

        credentials = f'Username: {username}\nPassword: {password}'
        credentials_with_spoiler = f'Username: {username}\nPassword: <tg-spoiler>{password}</tg-spoiler>'

        text = f'<b>User successfully created</b>\n\n{credentials_with_spoiler}'

        await message.answer(
            text=text,
            reply_markup=self._key_board.get_copy_button(
                text_btn='Copy credentials',
                text_to_copy=credentials
            )
        )

        await state.clear()

    async def _delete_user(self, message: Message, state: FSMContext):
        username = message.text.strip()

        try:
            await self._staff_service.delete_user(username)
        except UserNotFound:
            await message.answer('User not found')
            return

        await message.answer('User deleted successfully')
        await state.clear()
