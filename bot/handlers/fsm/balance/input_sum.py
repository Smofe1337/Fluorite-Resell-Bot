from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from bot.state.user import UserState
from bot.handlers.keyboard import KeyBoard
from bot.utils.maps import get_currency_by_lang
from bot.utils.converters import convertor
from bot.localization.localizer import localize


class BalanceInputRouter:
    def __init__(self, key_board: KeyBoard):
        self._key_board = key_board
        self.router = Router()
        self._register_routes()

    def _register_routes(self):
        self.router.message(UserState.wait_sum_to_up_balance)(self._input_sum_to_replenish)

    async def _input_sum_to_replenish(self, message: Message, state: FSMContext) -> None:
        lang = message.from_user.language_code
        amount = message.text

        if not amount.isdigit():
            await message.answer(
                text=await localize(lang, 'need_input_number_text')
            )
            await state.clear()
            return

        amount = float(amount)
        currency = get_currency_by_lang(lang)
        amount_usd = await convertor(currency, amount)

        await state.update_data(
            amount=amount,
            amount_usd=amount_usd,
            currency=currency
        )

        await message.answer(
            text=await localize(lang, 'select_paymethod_text'),
            reply_markup=self._key_board.get_payment_balance()
        )
