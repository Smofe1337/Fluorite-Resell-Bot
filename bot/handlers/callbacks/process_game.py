import os
from aiogram.types import Message, FSInputFile
from bot.database.service.games import GameService
from bot.handlers.keyboard import KeyBoard
from bot.core.exceptions import GameNotFound
from bot.localization.localizer import localize
from config import Config


class ProcessGames:
    def __init__(self, game_service: GameService, key_board: KeyBoard):
        self.game_service = game_service
        self.key_board = key_board
    

    async def select_duration(self, message: Message, game_name: str, lang: str) -> None:
        try:
            game = await self.game_service.get_game(game_name)
        except GameNotFound:
            await message.answer(
                text=await localize(lang, 'game_not_found_text')
            )
            return

        if game.is_need_show_img:
            photo = game.image_url
            if '/api/static/images/' in photo:
                filename = photo.split('/api/static/images/')[-1]
                path = os.path.join(Config.UPLOADED_IMAGES_PATH, filename)
                photo = FSInputFile(path)

            await message.answer_photo(
                photo=photo,
                caption=await localize(lang, 'select_duration_text'),
                reply_markup=await self.key_board.get_price(game_name, lang)
            )
        else:
            await message.answer(
                text=await localize(lang, 'select_duration_text'), 
                reply_markup=await self.key_board.get_price(game_name, lang)
            )

    
    async def select_paymethod(self, message: Message, game_name: str, days: int, lang: str) -> None:
        await message.answer(
            text=await localize(lang, 'select_paymethod_text'), 
            reply_markup=await self.key_board.get_payment(game_name, days, lang)
        )
    