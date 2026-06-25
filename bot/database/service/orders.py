import logging
from bot.database.repository.orders import OrdersRepository
from bot.database.service.users import UserService
from bot.database.service.keys import KeysService
from bot.enums.orders import OrderStatus, OrderType
from bot.enums.keys import KeyStatus
from config import Config
from typing import List, Dict

logger = logging.getLogger(__name__)


class OrdersService:
    def __init__(self, order_repo: OrdersRepository, user_service: UserService):
        self._order_repo = order_repo
        self._user_service = user_service

    async def new_order(self, data: Dict[str, any]):
        order_type = data['order_type']

        if order_type == OrderType.KEY.value:
            await self._order_repo.create_order(
                user_id=data['user_id'],
                order_id=data['order_id'],
                sum=data['sum'],
                payment_system_order_id=data['payment_system_order_id'],
                payment_method=data['payment_method'],
                order_type=order_type,
                pay_url=data['pay_url'],
                expired_at=data['expired_at'],
                is_gift=data['is_gift'],
                game_name=data['game_name'],
                duration=data['duration'],
            )

        elif order_type == OrderType.TOP_UP_BALANCE.value:
            await self._order_repo.create_order(
                user_id=data['user_id'],
                order_id=data['order_id'],
                sum=data['sum'],
                payment_system_order_id=data['payment_system_order_id'],
                payment_method=data['payment_method'],
                is_need_back_button=data['is_need_back_button'],
                order_type=order_type,
                pay_url=data['pay_url'],
                expired_at=data['expired_at'],
                game_name=data.get('game_name'),
                duration=data.get('duration'),
            )

        elif order_type == OrderType.GIFT.value:
            await self._order_repo.create_order(
                user_id=data['user_id'],
                order_id=data['order_id'],
                sum=data['sum'],
                payment_system_order_id=data['payment_system_order_id'],
                payment_method=data['payment_method'],
                order_type=order_type,
                pay_url=data['pay_url'],
                expired_at=data['expired_at'],
                is_gift=data['is_gift'],
                game_name=data['game_name'],
                duration=data['duration'],
            )

        elif order_type == OrderType.UNBAN.value:
            await self._order_repo.create_order(
                user_id=data['user_id'],
                order_id=data['order_id'],
                sum=data['sum'],
                payment_system_order_id=data['payment_system_order_id'],
                payment_method=data['payment_method'],
                order_type=order_type,
                pay_url=data['pay_url'],
                expired_at=data['expired_at'],
            )

    async def update_order(self, order_id: str, status: str, product: str | None = None):
        await self._order_repo.update_order(order_id, status=status, product=product)

    async def get_order_by_id(self, order_id: str):
        return await self._order_repo.get_order_by_id(order_id)

    async def get_order_by_system(self, system_order_id: str):
        return await self._order_repo.get_order_by_payment_system_id(system_order_id)

    async def on_success(
            self,
            key_service: KeysService,
            user_id: int,
            order_id: str,
            sum: float,
            order_type: str,
            key: str | None = None,
            token: str | None = None,
            invite_link: str | None = None,
    ):
        logger.info(f'Order {order_id} paid: user={user_id}, sum={sum}, type={order_type}')

        consumed_key: bool = False

        if order_type == OrderType.KEY.value:
            await key_service.update_key(key, KeyStatus.SOLD.value)
            await key_service.bind_key_to_user(user_id, key)
            consumed_key = True

        elif order_type == OrderType.GIFT.value:
            await key_service.update_key(key, KeyStatus.PENDING.value, token)
            consumed_key = True

        await self.update_order(order_id, OrderStatus.PAID.value, key)
        await self._user_service.handle_order(user_id, sum, invite_link)

        if consumed_key:
            await self._notify_low_stock(key_service, order_id)

    async def _notify_low_stock(self, key_service: KeysService, order_id: str) -> None:
        order = await self._order_repo.get_order_by_id(order_id)
        game_name: str | None = getattr(order, 'game_name', None)
        duration: int | None = getattr(order, 'duration', None)
        if game_name is None or duration is None:
            return

        remaining: int = await key_service.count_available(game_name, duration)
        if remaining > Config.LOW_STOCK_THRESHOLD:
            return
        if remaining != Config.LOW_STOCK_THRESHOLD and remaining != 0:
            return

        if remaining == 0:
            text = (
                '⚠️ <b>Out of stock</b>\n'
                f'Game: <b>{game_name}</b>\n'
                f'Duration: <b>{duration} days</b>'
            )
        else:
            text = (
                '⚠️ <b>Low stock</b>\n'
                f'Game: <b>{game_name}</b>\n'
                f'Duration: <b>{duration} days</b>\n'
                f'Remaining: <b>{remaining}</b>'
            )

        from bot.services.init_services import bot
        try:
            await bot.send_message(chat_id=Config.OWNER_ID, text=text)
        except Exception as e:
            logger.error(f'Failed to send low-stock alert: {e}')

    async def get_all_orders(self):
        return await self._order_repo.get_all_orders()

    async def get_orders_paginated(
        self,
        page: int = 1,
        per_page: int = 15,
        search: str | None = None,
        status: str | None = None,
    ) -> Dict:
        orders, total = await self._order_repo.get_orders_paginated(page, per_page, search, status)
        return {
            'orders': orders,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': -(-total // per_page),
        }

    async def get_orders_stats(self) -> Dict:
        return await self._order_repo.get_orders_stats()

    async def get_all_order_by_user(self, user_id: int) -> List[Dict]:
        return await self._order_repo.get_all_order_by_user(user_id)

    async def get_user_orders_paginated(self, user_id: int, page: int = 1, per_page: int = 5):
        return await self._order_repo.get_user_orders_paginated(user_id, page, per_page)

    async def get_status(self, order_id: str) -> str:
        return (await self._order_repo.get_order_by_id(order_id)).status
