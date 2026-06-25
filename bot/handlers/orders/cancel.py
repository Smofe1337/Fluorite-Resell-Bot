from aiogram.types import CallbackQuery
from bot.handlers.keyboard import KeyBoard
from bot.database.service.orders import OrdersService
from bot.payments.cryptobot import CryptoBot
from bot.utils.maps import get_days, get_currency_by_lang
from bot.enums.orders import OrderStatus, OrderType
from bot.localization.localizer import localize
from bot.utils.converters import convert_from_usd
from bot.utils.generator import generate_order_text, generate_order_text_balance


class OrderCancelHandler:
    def __init__(self, order_service: OrdersService, crypto_bot: CryptoBot, key_board: KeyBoard):
        self._order_service = order_service
        self._crypto_bot = crypto_bot
        self._key_board = key_board

    async def confirm_cancel_order(self, callback: CallbackQuery, order_id: str) -> None:
        lang = callback.from_user.language_code
        await callback.message.edit_text(
            text=await localize(lang, 'cancel_confirm_text', order_id),
            reply_markup=await KeyBoard.get_confirm_button(lang, order_id)
        )

    async def delete_order(self, callback: CallbackQuery, order_id: str) -> None:
        lang = callback.from_user.language_code
        order = await self._order_service.get_order_by_id(order_id)

        if order is not None:
            if order.payment_method == 'CryptoBot':
                await self._crypto_bot.delete(order.payment_system_order_id)
            await self._order_service.update_order(order_id, OrderStatus.CANCELLED.value)
        else:
            await callback.answer(
                text=await localize(lang, 'order_not_found_alert'),
                show_alert=True
            )
            return

        await callback.message.edit_text(
            text=await localize(lang, 'cancel_success_text', order_id),
            reply_markup=await KeyBoard.back_to_catalog(lang)
        )

    async def back_to_payment(self, callback: CallbackQuery, order_id: str) -> None:
        lang = callback.from_user.language_code
        currency = get_currency_by_lang(lang)

        order = await self._order_service.get_order_by_id(order_id)
        if order is not None:
            if order.order_type in [OrderType.KEY.value, OrderType.GIFT.value]:
                converted_amount = await convert_from_usd(currency, order.sum)

                text = await generate_order_text(
                    lang,
                    order_id,
                    f'{order.game_name} {await get_days(lang, order.duration)}',
                    pay_method=order.payment_method,
                    amount=int(converted_amount),
                    create_at=order.create_at.replace(microsecond=0),
                    pay_before=order.expired_at
                )

                await callback.message.edit_text(
                    text=text,
                    reply_markup=await self._key_board.get_pay(lang, order.pay_url, order_id),
                    disable_web_page_preview=True
                )

            elif order.order_type == OrderType.TOP_UP_BALANCE.value:
                converted_amount = await convert_from_usd(currency, order.sum)

                text = await generate_order_text_balance(
                    lang=lang,
                    order_id=order_id,
                    pay_method=order.payment_method,
                    amount=round(converted_amount, 2),
                    create_at=order.create_at,
                    pay_before=order.expired_at
                )

                await callback.message.edit_text(
                    text=text,
                    reply_markup=await self._key_board.get_pay(lang, order.pay_url, order_id),
                    disable_web_page_preview=True
                )
