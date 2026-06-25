from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from bot.database.service.users import UserService
from bot.database.service.orders import OrdersService
from bot.core.exceptions import UserNotFound
from bot.localization.localizer import localize
from bot.utils.maps import get_days, get_currency_by_lang
from bot.utils.converters import convert_from_usd

ORDERS_PER_PAGE = 5

STATUS_EMOJI = {
    'Paid': '✅',
    'Pending': '⏳',
    'Cancelled': '❌',
    'Expired': '⌛',
    'Error': '⚠️',
}


class OrderDownloadHandler:
    def __init__(self, user_service: UserService, order_service: OrdersService):
        self._user_service = user_service
        self._order_service = order_service

    async def _build_orders_message(self, user_id: int, lang: str, page: int = 1) -> tuple[str, InlineKeyboardMarkup | None]:
        orders, total = await self._order_service.get_user_orders_paginated(user_id, page, ORDERS_PER_PAGE)
        total_pages = max(1, -(-total // ORDERS_PER_PAGE))

        if not orders:
            return await localize(lang, 'my_orders_empty'), None

        text = await localize(lang, 'my_orders_title')

        for order in orders:
            game = order.game_name or order.order_type
            duration = await get_days(lang, order.duration) if order.duration else ''
            status_emoji = STATUS_EMOJI.get(order.status, '❓')
            currency = get_currency_by_lang(lang)
            converted = await convert_from_usd(currency, order.sum)
            symbol = '₽' if lang == 'ru' else '$'
            amount = f'{round(converted, 2)}{symbol}'
            date = order.create_at.strftime('%d.%m.%Y %H:%M')

            text += await localize(lang, 'my_orders_item', game, amount, status_emoji, order.order_id, date)

            if order.product and order.status == 'Paid':
                text += await localize(lang, 'my_orders_product', order.product)

        if total_pages > 1:
            text += await localize(lang, 'my_orders_page', page, total_pages)

        nav_buttons = []
        if page > 1:
            nav_buttons.append(InlineKeyboardButton(
                text=await localize(lang, 'my_orders_prev_btn'),
                callback_data=f'orders_page:{page - 1}'
            ))
        if page < total_pages:
            nav_buttons.append(InlineKeyboardButton(
                text=await localize(lang, 'my_orders_next_btn'),
                callback_data=f'orders_page:{page + 1}'
            ))

        rows = []
        if nav_buttons:
            rows.append(nav_buttons)
        rows.append([InlineKeyboardButton(
            text=await localize(lang, 'back_btn'), callback_data='back_to_profile'
        )])

        keyboard = InlineKeyboardMarkup(inline_keyboard=rows)
        return text, keyboard

    async def download_orders(self, callback: CallbackQuery):
        user_id = callback.from_user.id
        lang = callback.from_user.language_code

        try:
            if await self._user_service.is_banned(user_id):
                return
        except UserNotFound:
            await self._user_service.register_user(user_id, lang)

        text, keyboard = await self._build_orders_message(user_id, lang)
        await callback.message.delete()
        await callback.message.answer(text, reply_markup=keyboard)

    async def handle_page(self, callback: CallbackQuery):
        user_id = callback.from_user.id
        lang = callback.from_user.language_code
        page = int(callback.data.split(':')[1])

        text, keyboard = await self._build_orders_message(user_id, lang, page)
        await callback.message.edit_text(text, reply_markup=keyboard)
