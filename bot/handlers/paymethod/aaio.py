from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from datetime import datetime
from bot.database.service.games import GameService
from bot.database.service.orders import OrdersService
from bot.handlers.keyboard import KeyBoard
from bot.payments.aaio import Aaio
from bot.utils.maps import get_currency_by_lang, get_days, duration_map_int
from bot.utils.generator import get_order_id, generate_order_text, generate_order_text_balance
from bot.utils.converters import get_usd_price
from bot.utils.timezone import get_now
from bot.views.error_message import send_error_message
from bot.handlers.paymethod.data.parser import parse_data
from bot.localization.localizer import localize
from bot.core.exceptions import FailedCreatePayment, FailedParseResponse
from bot.enums.orders import OrderType, OrderStatus
import asyncio


class AaioPaymentHandler:
    def __init__(self, game_service: GameService, order_service: OrdersService, key_board: KeyBoard, aaio: Aaio):
        self._game_service = game_service
        self._order_service = order_service
        self._key_board = key_board
        self._aaio = aaio

    async def paymethod_aaio(self, callback: CallbackQuery, data: str, is_gift: bool) -> None:
        user_id = callback.from_user.id
        lang = callback.from_user.language_code
        message = callback.message

        currency = get_currency_by_lang(lang)
        usd_price = await get_usd_price()

        order_id = get_order_id()
        order_data = {
            'user_id': user_id,
            'order_id': order_id,
            'payment_method': 'Aaio',
            'is_gift': is_gift,
            'order_type': OrderType.KEY.value if not is_gift else OrderType.GIFT.value
        }

        game_name, duration_str = parse_data(data)

        order_data['game_name'] = game_name
        order_data['duration'] = duration_map_int.get(duration_str)

        game_prices = await self._game_service.get_game_price(game_name, currency, usd_price)
        all_prices = game_prices.get(currency)
        price = all_prices.get(f'price_{duration_str}')

        price_in_usd = game_prices['USD']
        price_to_db = price_in_usd[f'price_{duration_str}']
        order_data['sum'] = price_to_db

        try:
            pay_url, payment_id = await self._aaio.create_invoice(price, order_id, currency.upper(), lang)
            order_info = await self._aaio.get_order_info(order_id)
        except FailedCreatePayment:
            await send_error_message(message, '#05', lang)
            return
        except FailedParseResponse:
            await send_error_message(message, '#04', lang)
            return

        expired_date = datetime.strptime(order_info, '%Y-%m-%d %H:%M:%S')
        order_data['expired_at'] = expired_date

        time_now = get_now(lang)

        if expired_date and payment_id:
            order_data['payment_system_order_id'] = payment_id
            order_data['pay_url'] = pay_url
            await self._order_service.new_order(order_data)

            pay_text = await generate_order_text(
                lang,
                order_id,
                f'{game_name} {await get_days(lang, duration_map_int[duration_str])}',
                order_data['payment_method'],
                price,
                time_now.strftime('%Y-%m-%d %H:%M:%S'),
                expired_date
            )

            await message.edit_text(
                text=pay_text,
                reply_markup=await self._key_board.get_pay(lang, pay_url, order_id),
                disable_web_page_preview=True
            )

            while datetime.now() <= expired_date:
                time_left = (expired_date - datetime.now()).total_seconds()
                await asyncio.sleep(time_left)

                order = await self._order_service.get_order_by_id(order_id)
                if order.status in [OrderStatus.CANCELLED.value, OrderStatus.PAID.value]:
                    break

                await self._order_service.update_order(order_id, OrderStatus.EXPIRED.value)
                await message.answer(await localize(lang, 'payment_expired_text'))

    async def paymethod_aaio_balance(self, callback: CallbackQuery, state: FSMContext) -> None:
        user_id = callback.from_user.id
        lang = callback.from_user.language_code
        message = callback.message
        state_data = await state.get_data()

        order_id = get_order_id()
        order_data = {
            'user_id': user_id,
            'order_id': order_id,
            'payment_method': 'Aaio',
            'order_type': OrderType.TOP_UP_BALANCE.value
        }

        if state_data is not None:
            amount_to_balance = state_data.get('amount')
            amount_to_balance_usd = state_data.get('amount_usd')
            currency: str = state_data.get('currency')
            is_need_send_back_button = state_data.get('is_need_send_back_button', False)

            if all([amount_to_balance, amount_to_balance_usd, currency]):
                order_data['sum'] = amount_to_balance_usd
                order_data['is_need_back_button'] = is_need_send_back_button

                try:
                    pay_url, payment_id = await self._aaio.create_invoice(amount_to_balance, order_id, currency.upper(), lang)
                    order_info = await self._aaio.get_order_info(order_id)
                except FailedCreatePayment:
                    await send_error_message(message, '#05', lang)
                    return
                except FailedParseResponse:
                    await send_error_message(message, '#04', lang)
                    return

                time_now = get_now(lang)
                expired_date = datetime.strptime(order_info, '%Y-%m-%d %H:%M:%S')
                order_data['expired_at'] = expired_date

                if payment_id and expired_date:
                    order_data['payment_system_order_id'] = payment_id
                    order_data['pay_url'] = pay_url
                    await self._order_service.new_order(order_data)

                    pay_text = await generate_order_text_balance(
                        lang,
                        order_id,
                        'Aaio',
                        amount_to_balance,
                        time_now.strftime('%Y-%m-%d %H:%M:%S'),
                        expired_date
                    )

                    await message.edit_text(
                        text=pay_text,
                        reply_markup=await self._key_board.get_pay(lang, pay_url, order_id),
                        disable_web_page_preview=True
                    )
                    await state.clear()

                    while datetime.now() <= expired_date:
                        time_left = (expired_date - datetime.now()).total_seconds()
                        await asyncio.sleep(time_left)

                        order = await self._order_service.get_order_by_id(order_id)
                        if order.status in [OrderStatus.CANCELLED.value, OrderStatus.PAID.value]:
                            break

                        await self._order_service.update_order(order_id, OrderStatus.EXPIRED.value)
                        await message.answer(await localize(lang, 'payment_expired_text'))
