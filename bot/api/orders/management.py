from fastapi import APIRouter, Depends, Query
from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError
from bot.api.dashboard.oauth2.security import get_current_user
from bot.api.orders.schemes import UpdateStatus
from bot.core.error_handlers import hook_exceptions
from bot.localization.localizer import localize
from bot.enums.orders import OrderStatus
from bot.database.service.orders import OrdersService
from bot.database.service.users import UserService
from bot.payments.cryptobot import CryptoBot
from typing import Optional


class OrdersRouter:
    def __init__(self, order_service: OrdersService, user_service: UserService, crypto_bot: CryptoBot, bot: Bot):
        self._order_service = order_service
        self._user_service = user_service
        self._crypto_bot = crypto_bot
        self._bot = bot
        self.router = APIRouter(dependencies=[Depends(get_current_user)])
        self._register_routes()

    def _register_routes(self):
        self.router.get('/orders/')(self._get_all_orders)
        self.router.get('/orders/{order_id}/')(hook_exceptions(self._get_order))
        self.router.get('/orders/user/{user_id}/')(hook_exceptions(self._get_orders_by_user))
        self.router.get('/orders/stats/summary/')(self._get_orders_stats)
        self.router.post('/orders/update-status/')(hook_exceptions(self._update_status))

    async def _get_all_orders(
        self,
        page: int = Query(1, ge=1),
        per_page: int = Query(15, ge=1, le=100),
        search: Optional[str] = Query(None),
        status: Optional[str] = Query(None),
    ):
        return await self._order_service.get_orders_paginated(page, per_page, search, status)

    async def _get_order(self, order_id: str):
        order = await self._order_service.get_order_by_id(order_id)
        if not order:
            return {'Status': False, 'Message': 'Order not found'}
        return _order_to_dict(order)

    async def _get_orders_by_user(self, user_id: int):
        return await self._order_service.get_all_order_by_user(user_id)

    async def _get_orders_stats(self):
        return await self._order_service.get_orders_stats()

    async def _update_status(self, data: UpdateStatus):
        statuses = [status.value for status in OrderStatus]
        status = data.status

        if status not in statuses:
            return {'Error': 'Invalid status'}

        order_id = data.order_id
        await self._order_service.update_order(order_id, status)

        order = await self._order_service.get_order_by_id(order_id)
        if order.status == OrderStatus.CANCELLED.value:
            if order.payment_method == 'CryptoBot':
                await self._crypto_bot.delete(order.payment_system_order_id)

            try:
                user_id = order.user_id
                lang = await self._user_service.get_lang(user_id)
                await self._bot.send_message(
                    text=await localize(lang, 'order_cancel_msg', order_id),
                    chat_id=user_id
                )
            except TelegramForbiddenError:
                pass

        return {'Status': True, 'Message': 'Order status updated successfully'}


def _order_to_dict(order):
    return {
        'id': order.id,
        'user_id': order.user_id,
        'order_id': order.order_id,
        'game_name': order.game_name,
        'duration': order.duration,
        'sum': order.sum,
        'payment_system_order_id': order.payment_system_order_id,
        'pay_url': order.pay_url,
        'order_type': order.order_type,
        'payment_method': order.payment_method,
        'create_at': str(order.create_at),
        'expired_at': str(order.expired_at),
        'status': order.status,
        'is_gift': order.is_gift,
        'product': order.product,
    }
