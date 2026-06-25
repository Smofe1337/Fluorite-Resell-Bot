from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from bot.handlers.keyboard import KeyBoard
from bot.core.permission import admin_only

router = Router()


@router.message(Command('createcoupon'))
@admin_only
async def create_coupone_command(message: Message) -> None:
    await message.answer(
        'Please seletc coupon type', 
        reply_markup=KeyBoard.coupone_type()
    )
