# from abc import ABC, abstractmethod

from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from datetime import datetime

from bot.state.admins import CreateCoupon
from bot.enums.coupons import CouponTypes


class BaseCouponStrategy:
    async def start(self, message: Message, state: FSMContext) -> None:
        pass


    async def handle_vip_flag(self, callabck: CallbackQuery, state: FSMContext) -> None:
        vpi_flag = callabck.data.split(':') == 'vip'
        await state.update_data(vip_flag=vpi_flag)

        state_data = await state.get_data()
        coupon_type = state_data['coupon_type']
        
        if coupon_type == CouponTypes.KEY.value:
            from bot.services.init_services import key_coupon_strategy
            await key_coupon_strategy.handle_select_game(callabck, state)
            return
        
        await state.set_state(CreateCoupon.waiting_for_activation_limit)
        await callabck.message.delete()
        await callabck.message.answer('Enter activation limit')
    

    async def handle_activation_limit(self, message: Message, state: FSMContext) -> None:
        text = message.text
        if not text.isdigit():
            await message.answer('Please input number')
            return
        
        activation_limit = int(text)
        
        await state.update_data(activation_limit=activation_limit)
        await state.set_state(CreateCoupon.waiting_for_limit_per_user)
        
        await message.answer('Please enter the maximum number of redemptions per user')
    

    async def handle_limit_per_user(self, message: Message, state: FSMContext) -> None:
        text = message.text
        if not text.isdigit():
            await message.answer('Please input number')
            return
        
        max_redemptions_per_user = int(text)
        
        await state.update_data(max_redemptions_per_user=max_redemptions_per_user)
        await state.set_state(CreateCoupon.waiting_for_expires)
        
        await message.answer('Please enter the coupon expiration date and time\nExample: 2025-07-18 18:30')


    async def handle_expires(self, message: Message, state: FSMContext) -> None:
        text = message.text
        
        try:
            expires_at = datetime.strptime(text, '%Y-%m-%d %H:%M')
        except ValueError:
            await message.answer('Invalid format. Format should be: <b>YYYY-MM-DD HH:MM</b>')
            return
        
        if expires_at <= datetime.now():
            await message.answer(
                'The date must not be less than or current'
            )
            return
        
        await state.update_data(expires_at=expires_at)
        await self.finalize(message, state)


    async def finalize(self, message: Message, state: FSMContext) -> None:
        from bot.commands.admins.coupon_builder import build_coupone

        await build_coupone(message, state)
        await state.clear()
