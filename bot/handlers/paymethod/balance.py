from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.database.service.games import GameService
from bot.database.service.orders import OrdersService
from bot.database.service.keys import KeysService
from bot.database.service.users import UserService
from bot.handlers.keyboard import KeyBoard
from bot.core.exceptions import UserNotFound
from bot.handlers.paymethod.data.parser import parse_data
from bot.utils.maps import get_currency_by_lang, get_days, duration_map_int
from bot.utils.timezone import get_now
from bot.utils.generator import get_order_id
from bot.utils.converters import get_usd_price, convert_from_usd
from bot.utils.generator import generate_invite_link_to_channel
from bot.commands.gift_builder import build_gift_link
from bot.localization.localizer import localize
from bot.utils.generator import generate_balance_pay
from bot.views.error_message import send_error_message
from bot.enums.orders import OrderStatus, OrderType
from datetime import timedelta
from config import Config


class BalancePaymentHandler:
    def __init__(self, game_service: GameService, order_service: OrdersService, keys_service: KeysService,
                 user_service: UserService, key_board: KeyBoard):
        self._game_service = game_service
        self._order_service = order_service
        self._keys_service = keys_service
        self._user_service = user_service
        self._key_board = key_board

    async def paymethod_balance_create(self, callback: CallbackQuery, data: str, is_gift: bool, state: FSMContext) -> None:
        user_id = callback.from_user.id
        lang = callback.from_user.language_code
        message = callback.message

        currency = get_currency_by_lang(lang)
        usd_price = await get_usd_price()

        order_id = get_order_id()
        order_data = {
            'user_id': user_id,
            'order_id': order_id,
            'payment_system_order_id': order_id,
            'payment_method': 'Balance',
            'is_gift': is_gift,
            'order_type': OrderType.KEY.value if not is_gift else OrderType.GIFT.value
        }

        game_name, duration_str = parse_data(data)
        order_data['game_name'] = game_name
        game_prices = await self._game_service.get_game_price(game_name, currency, usd_price)

        price_in_usd = game_prices.get('USD')
        price_to_db = price_in_usd.get(f'price_{duration_str}')

        order_data['sum'] = price_to_db
        duration = duration_map_int.get(duration_str)
        order_data['duration'] = duration

        try:
            user = await self._user_service.get_user(user_id)
        except UserNotFound:
            await send_error_message(message, '#09', lang)
            return

        user_balance = user.balance
        if user_balance < price_to_db:
            converted_price = round(await convert_from_usd(currency, price_to_db), 2)
            converted_balance = round(await convert_from_usd(currency, user_balance), 2)
            need_to_top_up = round(converted_price - converted_balance, 2)

            await state.update_data(
                amount=need_to_top_up,
                amount_usd=price_to_db,
                currency=currency,
                game_name=game_name,
                duration_str=duration_str,
                is_gift_safe=is_gift,
                is_balance=True,
                is_need_send_back_button=True
            )

            await message.edit_text(
                text=await localize(
                    lang,
                    'insufficient_funds_text',
                    converted_price,
                    need_to_top_up,
                    converted_balance
                ),
                reply_markup=self._key_board.get_text_button(
                    text_button=(
                        await localize(lang, 'top_up_balance_btn'),
                        await localize(lang, 'back_btn')
                    ),
                    callback_data=('top_up_balance', 'back_to_paymethod'),
                    is_need_back=True
                )
            )

            return

        order_data['pay_url'] = Config.BOT_BASE_URL + f'?start=pay_{order_id}'

        time_now = get_now(lang)
        expired_at = time_now + timedelta(minutes=25)
        order_expired = expired_at.replace(tzinfo=None, microsecond=0)

        order_data['expired_at'] = order_expired
        await self._order_service.new_order(order_data)

        await message.edit_text(
            text=await generate_balance_pay(
                lang,
                order_id,
                f'{game_name} {await get_days(lang, duration)}',
                order_data['payment_method'],
                time_now.strftime('%Y-%m-%d %H:%M:%S')
            ),
            reply_markup=self._key_board.get_balance_payment(order_id)
        )

        await state.clear()

    async def paymethod_balance(self, callback: CallbackQuery, order_id: str):
        user_id = callback.from_user.id
        lang = callback.from_user.language_code
        message = callback.message

        order = await self._order_service.get_order_by_id(order_id)
        if order:
            if order.status in [OrderStatus.CANCELLED.value, OrderStatus.PAID.value]:
                return

            game_name = order.game_name
            duration = order.duration

            if order.is_gift:
                await build_gift_link(
                    message, self._keys_service, self._order_service,
                    user_id, game_name, duration, order_id, order.sum
                )
                await self._user_service.update_balance(user_id, order.sum, '-')
            else:
                key = await self._keys_service.get_key(game_name, duration)
                if key:
                    invite_link = await generate_invite_link_to_channel()
                    await message.edit_text(
                        text=await localize(lang, 'success_payment_text', key.key),
                        reply_markup=self._key_board.get_copy_button_with_link(
                            text_buttons=(
                                await localize(lang, 'copy_key_btn'),
                                await localize(lang, 'private_channel_btn')
                            ),
                            text_to_copy=key.key,
                            link=invite_link
                        )
                    )
                    await self._user_service.update_balance(user_id, order.sum, '-')
                    await self._order_service.on_success(
                        key_servie=self._keys_service,
                        user_id=user_id,
                        order_id=order_id,
                        sum=order.sum,
                        order_type=order.order_type,
                        key=key.key,
                        invite_link=invite_link
                    )
        else:
            await message.edit_text(
                text=await localize(lang, 'an_error_text', '#11'),
                reply_markup=self._key_board.get_link_button(
                    text_btn=await localize(lang, 'contact_support_btn'),
                    link=Config.ADMIN_LINK
                )
            )
