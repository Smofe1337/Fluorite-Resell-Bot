from aiogram.types import Message
from bot.database.service.coupons import CouponsService
from bot.database.service.keys import KeysService
from bot.database.service.users import UserService
from bot.handlers.keyboard import KeyBoard
from bot.utils.maps import get_days
from bot.localization.localizer import localize
from bot.utils.generator import generate_invite_link_to_channel
from bot.utils.converters import convert_from_usd
from bot.utils.maps import get_currency_by_lang
from bot.enums.keys import KeyStatus


class KeyCouponHandler:
    def __init__(self, coupons_service: CouponsService, keys_service: KeysService, user_service: UserService, key_board: KeyBoard):
        self._coupons_service = coupons_service
        self._keys_service = keys_service
        self._user_service = user_service
        self._key_board = key_board

    async def process(self, message: Message, coupon_code: str) -> None:
        user_id = message.from_user.id
        lang = message.from_user.language_code

        coupon = await self._coupons_service.get_coupon(coupon_code)

        game = coupon.game
        duration = coupon.duration

        key = await self._keys_service.get_key(game, duration)
        if key:
            text = f'{await localize(lang, "key_text", key.key)}\n' \
                   f'{await localize(lang, "game_text", key.game_name)}\n' \
                   f'{await localize(lang, "duration_text", await get_days(lang, key.duration))}'

            await self._keys_service.bind_key_to_user(user_id, key.key)
            await self._keys_service.update_key(key.key, KeyStatus.RECEIVED.value)

            invite_link = await generate_invite_link_to_channel()
            await self._user_service.bind_invite_link(user_id, invite_link)

            await message.answer(
                text=text,
                reply_markup=self._key_board.get_copy_button_with_link(
                    text_buttons=(
                        await localize(lang, 'copy_key_btn'),
                        await localize(lang, 'private_channel_btn')
                    ),
                    text_to_copy=key.key,
                    link=invite_link
                )
            )


class MoneyCouponHandler:
    def __init__(self, coupons_service: CouponsService, user_service: UserService):
        self._coupons_service = coupons_service
        self._user_service = user_service

    async def process(self, message: Message, coupon_code: str) -> None:
        user_id = message.from_user.id
        lang = message.from_user.language_code
        currency = get_currency_by_lang(lang)

        coupon = await self._coupons_service.get_coupon(coupon_code)
        amount = coupon.amount

        await self._user_service.update_balance(user_id, amount, '+')

        converted_amount = await convert_from_usd(currency, amount)

        balance = await self._user_service.get_balance(user_id)
        converted_balance = await convert_from_usd(currency, balance)

        await message.answer(
            text=await localize(
                lang,
                'success_activate_coupon_balance',
                round(converted_amount, 2),
                round(converted_balance, 2)
            )
        )
