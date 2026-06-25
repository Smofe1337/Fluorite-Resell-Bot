from aiogram.types import Message
from bot.localization.localizer import localize
from bot.services.init_services import key_board


async def send_game_message(message: Message, lang: str | None = None) -> None:
    lang = lang or message.from_user.language_code

    await message.answer(
        text=await localize(lang, 'select_game'),
        reply_markup=await key_board.get_game()
    )
