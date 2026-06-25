import logging
from bot.database.repository.coupons import CouponsRepository
from bot.database.service.users import UserService
from bot.core.exceptions import (
    InactiveCouponError,
    CouponRedemptionLimitExceededError,
    NonVipUserError,
    ExpiredCouponError,
    MaxUserRedemptionsExceededError,
)
from typing import Dict
from datetime import datetime

logger = logging.getLogger(__name__)


class CouponsService:
    def __init__(self, coupons_repo: CouponsRepository, user_service: UserService):
        self._coupons_repo = coupons_repo
        self._user_service = user_service

    async def create(self, data: Dict[str, any]) -> None:
        await self._coupons_repo.create(
            coupon_code=data['coupon'],
            coupon_type=data['coupon_type'],
            activation_limit=data['activation_limit'],
            max_redemptions_per_user=data['max_redemptions_per_user'],
            is_vip=data['is_vip'],
            expires_at=data['expires_at'],
            amount=data['amount'],
            game=data['game'],
            duration=data['duration'],
        )

    async def is_vip(self, coupon_code: str) -> bool:
        coupon = await self._coupons_repo.get_coupon(coupon_code)
        return coupon.is_vip

    async def can_activate_coupon(self, coupon_code: str, user_id: int) -> bool:
        coupon = await self._coupons_repo.get_coupon(coupon_code)
        user_coupon = await self._coupons_repo.get_user_coupon(user_id, coupon_code)

        if coupon.expires_at < datetime.now():
            raise ExpiredCouponError()

        if coupon.times_redeemed >= coupon.activation_limit:
            raise CouponRedemptionLimitExceededError()

        if coupon.is_vip:
            if not await self._user_service.is_vip(user_id):
                raise NonVipUserError()

        if not coupon.is_activate:
            raise InactiveCouponError()

        if user_coupon.redemption_count >= coupon.max_redemptions_per_user:
            raise MaxUserRedemptionsExceededError()

        return True

    async def on_use(self, coupon_code: str, user_id: int) -> None:
        if await self.can_activate_coupon(coupon_code, user_id):
            await self._coupons_repo.increment_times_redeemed(coupon_code)
            await self._coupons_repo.increment_user_redemption_count(user_id, coupon_code)

    async def deactivate(self, coupon_code: str) -> None:
        await self._coupons_repo.deactivate_coupon(coupon_code)

    async def get_type(self, coupon_code: str) -> str:
        coupon = await self._coupons_repo.get_coupon(coupon_code)
        return coupon.coupon_type

    async def get_coupon(self, coupon_code: str):
        return await self._coupons_repo.get_coupon(coupon_code)
