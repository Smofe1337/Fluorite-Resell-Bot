from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from bot.services.init_services import user_service, key_board
from bot.core.exceptions import UserNotFound
from bot.localization.localizer import localize
from config import Config


router = Router()


@router.message(Command('help'))
async def help_command(message: Message) -> None:
    user_id = message.from_user.id
    lang = message.from_user.language_code

    try:
        if await user_service.is_banned(user_id):
            return
    except UserNotFound:
        await user_service.register_user(user_id, lang)
    

    await message.answer(
        text=await localize(lang, 'help_text'),
        disable_web_page_preview=True,
        reply_markup=key_board.get_link_button(
            text_btn=await localize(lang, 'contact_support_btn'),
            link=Config.ADMIN_LINK
        )
    )
