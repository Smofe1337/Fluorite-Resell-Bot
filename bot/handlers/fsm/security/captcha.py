from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from bot.state.user import UserState
from bot.handlers.referral_system import ReferralHandler


class CaptchaRouter:
    def __init__(self, referral_handler: ReferralHandler):
        self._referral_handler = referral_handler
        self.router = Router()
        self._register_routes()

    def _register_routes(self):
        self.router.message(UserState.waiting_captcha)(self._handle_captcha)

    async def _handle_captcha(self, message: Message, state: FSMContext) -> None:
        await self._referral_handler.handle_captcha_answer(message, state)
