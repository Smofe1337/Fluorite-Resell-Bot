from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from bot.database.service.games import GameService
from bot.database.service.orders import OrdersService
from bot.handlers.keyboard import KeyBoard
from bot.payments.nicepay import NicePay
from bot.utils.generator import get_order_id
from bot.handlers.paymethod.data.parser import parse_data
from bot.enums.orders import OrderStatus, OrderType
from bot.utils.maps import get_days, duration_map_int
from bot.utils.generator import generate_order_text, generate_order_text_balance
from bot.utils.timezone import get_now
from bot.utils.maps import get_currency_by_lang
from bot.utils.converters import get_usd_price
from bot.core.exceptions import FailedCreatePayment, FailedParseResponse
from bot.localization.localizer import localize
from bot.views.error_message import send_error_message
from datetime import datetime
import asyncio
import time


class NicepayPaymentHandler:
    def __init__(self, game_service: GameService, order_service: OrdersService, nicepay: NicePay, key_board: KeyBoard):
        self._game_service = game_service
        self._order_service = order_service
        self._nicepay = nicepay
        self._key_board = key_board

    async def paymethod_nicepay(self, message: Message, data: str, email: str, is_gift: bool) -> None:
        user_id = message.from_user.id
        lang = message.from_user.language_code
        currency = get_currency_by_lang(lang)

        order_id = get_order_id()
        order_data = {
            'user_id': user_id,
            'order_id': order_id,
            'payment_method': 'NicePay',
            'is_gift': is_gift,
            'order_type': OrderType.KEY.value if not is_gift else OrderType.GIFT.value
        }

        game_name, duration_str = parse_data(data)

        order_data['game_name'] = game_name
        order_data['duration'] = duration_map_int.get(duration_str)

        game_prices = await self._game_service.get_game_price(game_name, currency, await get_usd_price())
        all_prices = game_prices.get(currency)
        price = all_prices.get(f'price_{duration_str}')

        prices_in_usd = game_prices['USD']
        price_to_db = prices_in_usd[f'price_{duration_str}']
        order_data['sum'] = price_to_db

        try:
            payment_id, pay_url, expired = await self._nicepay.create_payment(order_id, email, price, currency)
        except FailedCreatePayment:
            await send_error_message(message, '#05', lang)
            return
        except FailedParseResponse:
            await send_error_message(message, '#04', lang)
            return

        time_now = get_now(lang)
        time_for_pay = datetime.fromtimestamp(expired).strftime('%Y-%m-%d %H:%M:%S')
        order_data['expired_at'] = datetime.strptime(time_for_pay, '%Y-%m-%d %H:%M:%S')

        if order_id and payment_id:
            order_data['payment_system_order_id'] = payment_id
            order_data['pay_url'] = pay_url
            await self._order_service.new_order(order_data)

            pay_text = await generate_order_text(
                lang,
                order_id,
                f'{game_name} {await get_days(lang, duration_map_int.get(duration_str))}',
                order_data['payment_method'],
                price,
                time_now.strftime('%Y-%m-%d %H:%M:%S'),
                time_for_pay
            )

            await message.answer(
                text=pay_text,
                reply_markup=await self._key_board.get_pay(lang, pay_url, order_id),
                disable_web_page_preview=True
            )

            while time.time() <= expired:
                order = await self._order_service.get_order_by_id(order_id)

                time_left = expired - time.time()
                await asyncio.sleep(time_left)

                if order.status in [OrderStatus.CANCELLED.value, OrderStatus.PAID.value]:
                    break

                await self._order_service.update_order(order_id, OrderStatus.EXPIRED.value)
                await message.answer(await localize(lang, 'payment_expired_text'))

    async def paymethod_nicepay_balance(self, message: Message, email: str, state: FSMContext) -> None:
        user_id = message.from_user.id
        lang = message.from_user.language_code
        state_data = await state.get_data()
        await state.clear()

        order_id = get_order_id()

        order_data = {
            'user_id': user_id,
            'order_id': order_id,
            'payment_method': 'NicePay',
            'order_type': OrderType.TOP_UP_BALANCE.value
        }

        if state_data is not None:
            amount_to_balance = state_data.get('amount')
            amount_to_balance_usd = state_data.get('amount_usd')
            currency = state_data.get('currency')

            is_need_send_back_button = state_data.get('is_need_send_back_button', False)

            if is_need_send_back_button:
                game_name = state_data.get('game_name')
                duration_str = state_data.get('duration_str')

                if game_name and duration_str is not None:
                    order_data['game_name'] = game_name
                    order_data['duration'] = duration_map_int[duration_str]

            if amount_to_balance and amount_to_balance_usd and currency is not None:
                order_data['sum'] = amount_to_balance_usd
                order_data['is_need_back_button'] = is_need_send_back_button

                try:
                    payment_id, pay_url, expired = await self._nicepay.create_payment(order_id, email, amount_to_balance, currency)
                except FailedCreatePayment:
                    await send_error_message(message, '#05', lang)
                    return
                except FailedParseResponse:
                    await send_error_message(message, '#04', lang)
                    return

                if payment_id:
                    order_data['payment_system_order_id'] = payment_id
                    order_data['pay_url'] = pay_url
                    await self._order_service.new_order(order_data)
                    time_now = get_now(lang)
                    time_for_pay = datetime.fromtimestamp(expired).strftime('%Y-%m-%d %H:%M:%S')
                    order_data['expired_at'] = datetime.strptime(time_for_pay, '%Y-%m-%d %H:%M:%S')

                    pay_text = await generate_order_text_balance(
                        lang,
                        order_id,
                        order_data['payment_method'],
                        amount_to_balance,
                        time_now.strftime('%Y-%m-%d %H:%M:%S'),
                        time_for_pay
                    )

                    await message.answer(text=pay_text, reply_markup=await self._key_board.get_pay(lang, pay_url, order_id))

                    while time.time() <= expired:
                        order = await self._order_service.get_order_by_id(order_id)

                        time_left = expired - time.time()
                        await asyncio.sleep(time_left)

                        if order.status in [OrderStatus.CANCELLED.value, OrderStatus.PAID.value]:
                            break

                        await self._order_service.update_order(order_id, OrderStatus.EXPIRED.value)
                        await message.answer(
                            text=await localize(lang, 'payment_expired_text')
                        )
