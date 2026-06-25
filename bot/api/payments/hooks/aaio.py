from fastapi import APIRouter, Request, HTTPException, status, Form
from aiogram.exceptions import TelegramForbiddenError
from typing import Annotated
from bot.api.net.ip import get_client_ip
from bot.api.payments.hash.verify import verif_sign
from bot.utils.converters import convert_from_usd
from bot.api.payments.hooks.schemes import FormDataAaio
from bot.payments.aaio import Aaio
from bot.enums.orders import OrderStatus, OrderType
from bot.utils.maps import get_currency_by_lang, duration_map_string
from bot.localization.localizer import localize
from bot.utils.generator import get_random_string, generate_invite_link_to_channel
from config import Config
from aiogram import Bot
from bot.database.service.orders import OrdersService
from bot.database.service.users import UserService
from bot.database.service.keys import KeysService
from bot.handlers.keyboard import KeyBoard


class AaioHookRouter:
    def __init__(self, order_service: OrdersService, user_service: UserService, bot: Bot, key_board: KeyBoard, keys_service: KeysService, aaio: Aaio):
        self._order_service = order_service
        self._user_service = user_service
        self._bot = bot
        self._key_board = key_board
        self._keys_service = keys_service
        self._aaio = aaio
        self.router = APIRouter()
        self._register_routes()

    def _register_routes(self):
        self.router.post('/aaio/')(self._hook_aaio)

    async def _hook_aaio(self, form_data: Annotated[FormDataAaio, Form()], request: Request):
        order_id = form_data.order_id
        currency = form_data.currency

        order = await self._order_service.get_order_by_id(order_id)
        if order is not None:
            if order.status in [OrderStatus.PAID.value, OrderStatus.CANCELLED.value, OrderStatus.EXPIRED.value]:
                return

            if form_data.status in ['success', 'hold']:
                valid_ip_address = await self._aaio.get_valid_ip_address()
                client_ip_address = get_client_ip(request)

                if client_ip_address not in valid_ip_address:
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='hacking attempt')

                if not verif_sign(form_data.sign, form_data.amount, currency, order_id):
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='wrong sign')

                user_id = order.user_id
                user = await self._user_service.get_user(user_id)
                if user:
                    user_lang = user.lang
                    user_currency = get_currency_by_lang(user_lang)

                    if order.order_type == OrderType.UNBAN.value:
                        await self._handle_unban(user_id, user_lang, order_id)
                    elif order.order_type == OrderType.TOP_UP_BALANCE.value:
                        await self._handle_balance(user_id, user_lang, user_currency, order, order_id)
                    elif order.is_gift:
                        await self._handle_gift(user_id, user_lang, order, order_id)
                    else:
                        await self._handle_key(user_id, user_lang, order, order_id)

    async def _handle_unban(self, user_id: int, lang: str, order_id: str):
        await self._user_service.set_user_ban_status(user_id, False)
        await self._order_service.update_order(order_id, OrderStatus.PAID.value)

        try:
            await self._bot.send_message(
                chat_id=user_id,
                text=await localize(lang, 'referral_unban_success_text'),
            )
        except TelegramForbiddenError:
            pass

    async def _handle_balance(self, user_id: int, lang: str, currency: str, order, order_id: str):
        await self._user_service.update_balance(user_id, order.sum, '+')
        user_balance = await self._user_service.get_balance(user_id)

        try:
            amount_to_balance = await convert_from_usd(currency, order.sum)
            converted_balance = await convert_from_usd(currency, user_balance)

            if order.is_need_back_button:
                await self._bot.send_message(
                    chat_id=user_id,
                    text=await localize(
                        lang, 'success_payment_balance_text',
                        round(amount_to_balance, 2),
                        round(converted_balance, 2)
                    ),
                    reply_markup=await self._key_board.get_back_button(
                        lang, order.game_name, duration_map_string[order.duration]
                    )
                )
            else:
                await self._bot.send_message(
                    chat_id=user_id,
                    text=await localize(
                        lang, 'success_payment_balance_text',
                        round(amount_to_balance, 2),
                        round(converted_balance, 2)
                    )
                )
        except TelegramForbiddenError:
            pass

        await self._order_service.on_success(
            self._keys_service, user_id, order_id,
            order.sum, OrderType.TOP_UP_BALANCE.value
        )

    async def _handle_gift(self, user_id: int, lang: str, order, order_id: str):
        token = get_random_string()
        key = await self._keys_service.get_key(order.game_name, order.duration)

        if key:
            link = Config.BOT_BASE_URL + f'?start=gift_{token}'
            try:
                await self._bot.send_message(
                    chat_id=user_id,
                    text=await localize(lang, 'success_payment_gift_text', link),
                    reply_markup=self._key_board.get_copy_button(
                        text_btn=await localize(lang, 'copy_link_btn'),
                        text_to_copy=link
                    )
                )
            except TelegramForbiddenError:
                pass

            await self._order_service.on_success(
                self._keys_service, user_id, order_id,
                order.sum, OrderType.GIFT.value, key.key, token
            )
        else:
            try:
                await self._bot.send_message(
                    chat_id=user_id,
                    text=await localize(lang, 'key_not_found_text'),
                    reply_markup=self._key_board.get_link_button(
                        await localize(lang, 'contact_support_btn'), Config.ADMIN_LINK
                    )
                )
            except TelegramForbiddenError:
                pass

    async def _handle_key(self, user_id: int, lang: str, order, order_id: str):
        key = await self._keys_service.get_key(order.game_name, order.duration)
        invite_link = await generate_invite_link_to_channel()

        if key:
            try:
                await self._bot.send_message(
                    chat_id=user_id,
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
            except TelegramForbiddenError:
                pass

            await self._order_service.on_success(
                self._keys_service, user_id, order_id,
                order.sum, OrderType.KEY.value, key.key, invite_link=invite_link
            )
        else:
            try:
                await self._bot.send_message(
                    chat_id=user_id,
                    text=await localize(lang, 'key_not_found_text'),
                    reply_markup=self._key_board.get_link_button(
                        await localize(lang, 'contact_support_btn'), Config.ADMIN_LINK
                    )
                )
            except TelegramForbiddenError:
                pass
