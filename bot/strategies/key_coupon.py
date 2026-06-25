from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from .base import BaseCouponStrategy

from bot.state.admins import CreateCoupon
from bot.handlers.keyboard import KeyBoard


class KeyCouponStrategy(BaseCouponStrategy):
    def __init__(self, keyboard: KeyBoard):
        self.keyboard = keyboard


    async def start(self, message: Message, state: FSMContext) -> None:
        await state.set_state(CreateCoupon.waiting_for_vip_flag)
        await message.answer('This coupon is for VIP users only?',
                             reply_markup=KeyBoard.get_vip_flag())
    
    async def handle_select_game(self, callback: CallbackQuery, state: FSMContext) -> None:
        await callback.message.edit_text(
            'Select game', 
            reply_markup=await self.keyboard.get_games_coupon()
        )

    async def handle_select_duration(self, callback: CallbackQuery, state: FSMContext) -> None:
        await callback.message.edit_text(
            'Select duration',
            reply_markup=KeyBoard.get_duration_coupon()
        )
        
