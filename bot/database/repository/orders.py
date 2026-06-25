import logging
from sqlalchemy import select, update, func, or_, cast, String
from bot.database.models.orders import Orders
from bot.database.repository.base import BaseRepository
from typing import List, Dict, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class OrdersRepository(BaseRepository):

    async def create_order(
            self,
            user_id: int,
            order_id: str,
            sum: float,
            payment_method: str,
            payment_system_order_id: str,
            order_type: str,
            pay_url: str,
            expired_at: datetime,
            is_need_back_button: Optional[bool] = None,
            is_gift: Optional[bool] = None,
            game_name: Optional[str] = None,
            duration: Optional[int] = None,
    ):
        async with self._session() as session:
            new_order = Orders(
                user_id=user_id,
                order_id=order_id,
                game_name=game_name,
                duration=duration,
                sum=sum,
                payment_method=payment_method,
                payment_system_order_id=payment_system_order_id,
                order_type=order_type,
                pay_url=pay_url,
                expired_at=expired_at,
                is_gift=is_gift,
                is_need_back_button=is_need_back_button,
            )
            session.add(new_order)
            await session.commit()

    async def get_order_by_id(self, order_id: str):
        async with self._session() as session:
            result = await session.execute(select(Orders).where(Orders.order_id == order_id))
            return result.scalars().first()

    async def get_order_by_payment_system_id(self, payment_system_order_id: str):
        async with self._session() as session:
            result = await session.execute(
                select(Orders).where(Orders.payment_system_order_id == payment_system_order_id)
            )
            return result.scalars().first()

    async def update_order(self, order_id: str, status: str, product: str | None = None):
        async with self._session() as session:
            await session.execute(
                update(Orders).where(Orders.order_id == order_id).values(status=status, product=product)
            )
            await session.commit()

    async def get_all_orders(self) -> List[Dict]:
        async with self._session() as session:
            result = await session.execute(select(Orders))
            return [Orders.orm_to_dict(order) for order in result.scalars().all()]

    async def get_orders_paginated(
        self,
        page: int = 1,
        per_page: int = 15,
        search: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Tuple[List[Dict], int]:
        async with self._session() as session:
            query = select(Orders)
            count_query = select(func.count(Orders.id))

            if status:
                query = query.where(Orders.status == status)
                count_query = count_query.where(Orders.status == status)

            if search:
                search_filter = or_(
                    Orders.order_id.ilike(f'%{search}%'),
                    cast(Orders.user_id, String).ilike(f'%{search}%'),
                    Orders.game_name.ilike(f'%{search}%'),
                )
                query = query.where(search_filter)
                count_query = count_query.where(search_filter)

            total = (await session.execute(count_query)).scalar()

            query = query.order_by(Orders.id.desc())
            query = query.offset((page - 1) * per_page).limit(per_page)

            result = await session.execute(query)
            orders = [Orders.orm_to_dict(order) for order in result.scalars().all()]

            return orders, total

    async def get_orders_stats(self) -> Dict:
        async with self._session() as session:
            total = (await session.execute(select(func.count(Orders.id)))).scalar()
            paid = (await session.execute(
                select(func.count(Orders.id)).where(Orders.status == 'Paid')
            )).scalar()
            pending = (await session.execute(
                select(func.count(Orders.id)).where(Orders.status == 'Pending')
            )).scalar()
            cancelled = (await session.execute(
                select(func.count(Orders.id)).where(Orders.status == 'Cancelled')
            )).scalar()
            revenue = (await session.execute(
                select(func.coalesce(func.sum(Orders.sum), 0)).where(Orders.status == 'Paid')
            )).scalar()

            return {
                'total': total,
                'paid': paid,
                'pending': pending,
                'cancelled': cancelled,
                'revenue': round(float(revenue), 2),
            }

    async def get_all_order_by_user(self, user_id: int) -> List[Dict]:
        async with self._session() as session:
            result = await session.execute(select(Orders).where(Orders.user_id == user_id))
            return [
                Orders.orm_to_dict(
                    order,
                    exclude=[
                        'user_id', 'order_type', 'payment_system_order_id',
                        'is_need_back_button', 'is_gift', 'id',
                    ],
                    skip_none=True,
                )
                for order in result.scalars().all()
            ]

    async def get_user_orders_paginated(self, user_id: int, page: int = 1, per_page: int = 5) -> Tuple[List, int]:
        async with self._session() as session:
            count = (await session.execute(
                select(func.count(Orders.id)).where(Orders.user_id == user_id)
            )).scalar()

            result = await session.execute(
                select(Orders)
                .where(Orders.user_id == user_id)
                .order_by(Orders.id.desc())
                .offset((page - 1) * per_page)
                .limit(per_page)
            )

            return result.scalars().all(), count
