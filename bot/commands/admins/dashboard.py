from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from bot.state.admins import CreateUser, DeleteUser
from bot.core.permission import admin_only

router = Router()


@router.message(Command('createuser'))
@admin_only
async def create_user_command(message: Message, state: FSMContext) -> None:
    await state.set_state(CreateUser.input_username)
    await message.answer('<b>Input username</b>')
  

@router.message(Command('deluser'))
@admin_only
async def delete_user_command(message: Message, state: FSMContext) -> None:
    await state.set_state(DeleteUser.input_username)
    await message.answer('<b>Input username</b>')
