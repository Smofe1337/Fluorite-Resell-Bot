from aiogram.types import Message
from bot.utils.generator import get_welcome_photo, get_welcome_text
from bot.services.init_services import key_board


async def send_welcome(message: Message):
    lang = message.from_user.language_code
    first_name = message.from_user.first_name

    welcome_photo = get_welcome_photo(first_name)
    welcome_text = await get_welcome_text(lang, first_name)

    await message.answer_photo(
        photo=welcome_photo,
        caption=welcome_text,
        reply_markup=await key_board.get_main(lang)
    )
