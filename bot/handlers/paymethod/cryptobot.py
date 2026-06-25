from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.database.service.games import GameService
from bot.database.service.orders import OrdersService
from bot.database.service.keys import KeysService
from bot.database.service.users import UserService
from bot.handlers.keyboard import KeyBoard
from bot.payments.cryptobot import CryptoBot
from bot.utils.generator import get_order_id
from bot.utils.generator import generate_order_text, generate_order_text_balance
from bot.utils.timezone import get_now
from bot.utils.maps import get_days, duration_map_int
from bot.handlers.paymethod.data.parser import parse_data
from bot.enums.orders import OrderType
from bot.utils.maps import get_currency_by_lang
from bot.utils.converters import get_usd_price
from bot.views.error_message import send_error_message
from datetime import timedelta
from config import Config


class CryptobotPaymentHandler:
    def __init__(self, game_service: GameService, order_service: OrdersService, key_board: KeyBoard,
                 keys_service: KeysService, crypto_bot: CryptoBot, user_service: UserService):
        self._game_service = game_service
        self._order_service = order_service
        self._key_board = key_board
        self._keys_service = keys_service
        self._crypto_bot = crypto_bot
        self._user_service = user_service

    async def paymethod_cryptobot(self, callback: CallbackQuery, data: str, is_gift: bool) -> None:
        user_id = callback.from_user.id
        lang = callback.from_user.language_code
        message = callback.message
        currency = get_currency_by_lang(lang)

        order_id = get_order_id()

        order_data = {
            'user_id': user_id,
            'order_id': order_id,
            'payment_method': 'CryptoBot',
            'is_gift': is_gift,
            'order_type': OrderType.KEY.value if not is_gift else OrderType.GIFT.value
        }

        game_name, duration_str = parse_data(data)
        order_data['game_name'] = game_name
        game_prices = await self._game_service.get_game_price(game_name, currency, await get_usd_price())
        all_prices = game_prices.get(currency)
        price = all_prices.get(f'price_{duration_str}')

        prices_in_usd = game_prices.get('USD')
        price_to_db = prices_in_usd.get(f'price_{duration_str}')

        order_data['sum'] = price_to_db
        duration = duration_map_int.get(duration_str)
        order_data['duration'] = duration

        invoice = await self._crypto_bot.create_invoice(price, currency)

        if not invoice:
            await send_error_message(message, '#05', lang)
            return

        invoice_id, pay_url = invoice
        time_now = get_now(lang)
        order_expired = time_now + timedelta(minutes=25)

        order_data['payment_system_order_id'] = str(invoice_id)
        order_data['pay_url'] = pay_url
        order_data['expired_at'] = order_expired.replace(tzinfo=None, microsecond=0)
        await self._order_service.new_order(order_data)

        order_text = await generate_order_text(
            lang,
            order_id,
            f'{game_name} {await get_days(lang, duration)}',
            order_data['payment_method'],
            price,
            time_now.strftime('%Y-%m-%d %H:%M:%S'),
            order_expired.strftime('%Y-%m-%d %H:%M:%S')
        )

        await message.edit_text(
            order_text,
            reply_markup=await self._key_board.get_pay(lang, pay_url, order_id),
            disable_web_page_preview=True
        )

    async def paymethod_cryptobot_balance(self, callback: CallbackQuery, state: FSMContext) -> None:
        user_id = callback.from_user.id
        lang = callback.from_user.language_code
        message = callback.message
        state_data = await state.get_data()

        order_id = get_order_id()
        order_data = {
            'user_id': user_id,
            'order_id': order_id,
            'payment_method': 'CryptoBot',
            'is_gift': False,
            'order_type': OrderType.TOP_UP_BALANCE.value
        }

        if state_data is None:
            return

        amount_to_balance = state_data.get('amount')
        amount_to_balance_usd = state_data.get('amount_usd')
        currency = state_data.get('currency')
        is_need_send_back_button = state_data.get('is_need_send_back_button', False)

        order_data['sum'] = amount_to_balance_usd
        order_data['is_need_back_button'] = is_need_send_back_button

        if not amount_to_balance or currency is None:
            return

        invoice = await self._crypto_bot.create_invoice(amount_to_balance, currency)
        if not invoice:
            await send_error_message(message, '#05', lang)
            return

        invoice_id, pay_url = invoice
        time_now = get_now(lang)
        order_expired = time_now + timedelta(minutes=25)

        order_data['payment_system_order_id'] = str(invoice_id)
        order_data['pay_url'] = pay_url
        order_data['expired_at'] = order_expired.replace(tzinfo=None, microsecond=0)

        if is_need_send_back_button:
            order_data['game_name'] = state_data.get('game_name')
            order_data['duration'] = state_data.get('duration')

        await self._order_service.new_order(order_data)

        order_text = await generate_order_text_balance(
            lang,
            order_id,
            order_data['payment_method'],
            amount_to_balance,
            time_now.strftime('%Y-%m-%d %H:%M:%S'),
            order_expired.strftime('%Y-%m-%d %H:%M:%S')
        )

        await message.edit_text(
            text=order_text,
            reply_markup=await self._key_board.get_pay(lang, pay_url, order_id),
            disable_web_page_preview=True
        )

        await state.clear()
