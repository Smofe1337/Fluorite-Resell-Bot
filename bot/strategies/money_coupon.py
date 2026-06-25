from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.state.admins import CreateCoupon
from bot.handlers.keyboard import KeyBoard

from .base import BaseCouponStrategy

class MoneyCouponStrategy(BaseCouponStrategy):
    pass
    

    async def start(self, message: Message, state: FSMContext) -> None:
        await state.set_state(CreateCoupon.waiting_for_amount)
        await message.answer('Please input amount')
    

    async def handle_amount(self, message: Message, state: FSMContext) -> None:
        text = message.text
        if not text.isdigit():
            await message.answer('Please input a valid number')
            return
        
        amont = int(text)
        if amont <= 0:
            await message.answer('Amount must be greater than 0')
            return
     
        await state.update_data(amount=amont)
        await message.answer('This coupon is for VIP users only?',
                             reply_markup=KeyBoard.get_vip_flag())
    