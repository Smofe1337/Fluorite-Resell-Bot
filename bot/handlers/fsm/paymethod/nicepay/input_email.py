from aiogram import Router
from aiogram.types import Message
from email_validator import validate_email, EmailNotValidError
from aiogram.fsm.context import FSMContext
from bot.state.payments import Payments
from bot.handlers.paymethod.nicepay.nicepay import NicepayPaymentHandler
from bot.localization.localizer import localize


class NicepayEmailRouter:
    def __init__(self, nicepay_payment: NicepayPaymentHandler):
        self._nicepay_payment = nicepay_payment
        self.router = Router()
        self._register_routes()

    def _register_routes(self):
        self.router.message(Payments.request_email)(self._process_email)

    async def _process_email(self, message: Message, state: FSMContext) -> None:
        email = message.text.strip()
        lang = message.from_user.language_code

        if email:
            try:
                validate_email(email)
            except EmailNotValidError:
                await state.clear()
                await message.answer(
                    text=await localize(lang, 'email_not_valid_text')
                )
                return

        state_data = await state.get_data()

        if state_data.get('is_balance'):
            await self._nicepay_payment.paymethod_nicepay_balance(message, email, state)
            await state.clear()
            return

        await self._nicepay_payment.paymethod_nicepay(
            message,
            state_data.get('callback_data'),
            email,
            state_data.get('is_gift')
        )

        await state.clear()
