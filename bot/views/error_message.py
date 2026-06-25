from aiogram.types import Message
from bot.services.init_services import key_board
from bot.localization.localizer import localize
from config import Config


async def send_error_message(message: Message, error_code: str, lang: str) -> None:
    await message.answer(
        text=await localize(
            lang, 'an_error_text', error_code
        ),
        reply_markup=key_board.get_link_button(
            text_btn=await localize(lang, 'contact_support_btn'),
            link=Config.ADMIN_LINK
        ),
        disable_web_page_preview=True
    )
