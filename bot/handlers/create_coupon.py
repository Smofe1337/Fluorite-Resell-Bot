from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from bot.state.admins import CreateCoupon
from bot.strategies.base import BaseCouponStrategy
from bot.strategies.money_coupon import MoneyCouponStrategy


class CreateCouponRouter:
    def __init__(self, money_coupon_strategy: MoneyCouponStrategy, base_coupon_strategy: BaseCouponStrategy):
        self._money_coupon_strategy = money_coupon_strategy
        self._base_coupon_strategy = base_coupon_strategy
        self.router = Router()
        self._register_routes()

    def _register_routes(self):
        self.router.message(CreateCoupon.waiting_for_amount)(self._handle_amount)
        self.router.message(CreateCoupon.waiting_for_activation_limit)(self._handle_activation_limit)
        self.router.message(CreateCoupon.waiting_for_limit_per_user)(self._handle_limit_per_user)
        self.router.message(CreateCoupon.waiting_for_expires)(self._handle_expires)

    async def _handle_amount(self, message: Message, state: FSMContext) -> None:
        await self._money_coupon_strategy.handle_amount(message, state)

    async def _handle_activation_limit(self, message: Message, state: FSMContext):
        await self._base_coupon_strategy.handle_activation_limit(message, state)

    async def _handle_limit_per_user(self, message: Message, state: FSMContext):
        await self._base_coupon_strategy.handle_limit_per_user(message, state)

    async def _handle_expires(self, message: Message, state: FSMContext):
        await self._base_coupon_strategy.handle_expires(message, state)
