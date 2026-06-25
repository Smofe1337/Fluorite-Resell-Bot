import logging
from sqlalchemy import select, and_
from bot.database.models.coupons import Coupons, CouponsUsers
from bot.database.repository.base import BaseRepository
from bot.core.exceptions import CouponAlreadyExists, CouponNotFound
from datetime import datetime

logger = logging.getLogger(__name__)


class CouponsRepository(BaseRepository):

    async def is_coupon_exists(self, coupon_code: str) -> bool:
        async with self._session() as session:
            result = await session.execute(select(Coupons).where(Coupons.coupone == coupon_code))
            return result.scalar_one_or_none() is not None

    async def is_user_coupon_exists(self, user_id: int, coupon_code: str) -> bool:
        async with self._session() as session:
            result = await session.execute(select(CouponsUsers).where(and_(
                CouponsUsers.user_id == user_id,
                CouponsUsers.coupone == coupon_code,
            )))
            return result.scalar_one_or_none() is not None

    async def add_user(self, user_id: int, coupon_code: str) -> None:
        async with self._session() as session:
            new_user = CouponsUsers(user_id=user_id, coupone=coupon_code)
            session.add(new_user)
            await session.commit()

    async def create(
            self,
            coupon_code: str,
            coupon_type: str,
            activation_limit: int,
            max_redemptions_per_user: int,
            is_vip: bool,
            expires_at: datetime,
            amount: float | None,
            game: str | None,
            duration: int | None,
    ):
        if await self.is_coupon_exists(coupon_code):
            raise CouponAlreadyExists()

        async with self._session() as session:
            new_coupon = Coupons(
                coupone=coupon_code,
                coupon_type=coupon_type,
                activation_limit=activation_limit,
                max_redemptions_per_user=max_redemptions_per_user,
                is_vip=is_vip,
                expires_at=expires_at,
                amount=amount,
                game=game,
                duration=duration,
            )
            session.add(new_coupon)
            await session.commit()

    async def get_coupon(self, coupon_code: str) -> Coupons:
        if not await self.is_coupon_exists(coupon_code):
            raise CouponNotFound()

        async with self._session() as session:
            result = await session.execute(select(Coupons).where(Coupons.coupone == coupon_code))
            return result.scalars().first()

    async def get_user_coupon(self, user_id: int, coupon_code: str) -> CouponsUsers:
        if not await self.is_user_coupon_exists(user_id, coupon_code):
            await self.add_user(user_id, coupon_code)

        async with self._session() as session:
            result = await session.execute(select(CouponsUsers).where(and_(
                CouponsUsers.user_id == user_id,
                CouponsUsers.coupone == coupon_code,
            )))
            return result.scalars().first()

    async def increment_times_redeemed(self, coupon_code: str) -> None:
        if not await self.is_coupon_exists(coupon_code):
            raise CouponNotFound()

        async with self._session() as session:
            result = await session.execute(
                select(Coupons).where(Coupons.coupone == coupon_code).with_for_update()
            )
            coupon = result.scalars().first()
            coupon.times_redeemed += 1
            await session.commit()

    async def increment_user_redemption_count(self, user_id: int, coupon_code: str) -> None:
        if not await self.is_coupon_exists(coupon_code):
            raise CouponNotFound()

        if not await self.is_user_coupon_exists(user_id, coupon_code):
            await self.add_user(user_id, coupon_code)

        async with self._session() as session:
            result = await session.execute(select(CouponsUsers).where(and_(
                CouponsUsers.user_id == user_id,
                CouponsUsers.coupone == coupon_code,
            )).with_for_update())
            user = result.scalars().first()
            user.redemption_count += 1
            await session.commit()

    async def deactivate_coupon(self, coupon_code: str) -> None:
        if not await self.is_coupon_exists(coupon_code):
            raise CouponNotFound()

        async with self._session() as session:
            result = await session.execute(select(Coupons).where(Coupons.coupone == coupon_code))
            coupon = result.scalars().first()
            coupon.is_activate = False
            await session.commit()
