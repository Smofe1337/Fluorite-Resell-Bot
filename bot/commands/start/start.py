from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from bot.services.init_services import user_service, logger
from bot.commands.start.parser import parse_argument
from bot.views.welcome_sender import send_welcome
from bot.core.exceptions import UserNotFound

router = Router()


@router.message(Command('start'))
async def start_command(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    lang = message.from_user.language_code
    args = message.text.split('_')

    if len(args) == 2:
        func, data = parse_argument(args)
        if func and data is not None:
            from bot.handlers.register import start_argument_handler
            await start_argument_handler.handle_argument(message, func, data, state)
            return

    tg_user = message.from_user
    try:
        user_info = await user_service.get_user_info(user_id)
        await user_service.update_profile(
            user_id,
            username=tg_user.username,
            first_name=tg_user.first_name,
            last_name=tg_user.last_name,
            lang=lang,
        )
    except UserNotFound:
        await user_service.register_user(
            user_id, lang,
            username=tg_user.username,
            first_name=tg_user.first_name,
            last_name=tg_user.last_name,
        )
        await send_welcome(message)
        await logger.send_log(user_id, 'New user registered')
        return

    if user_info['is_banned']:
        return

    await send_welcome(message)
