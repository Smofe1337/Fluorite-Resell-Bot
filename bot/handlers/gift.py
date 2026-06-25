from aiogram.types import Message
from bot.database.service.keys import KeysService
from bot.database.service.users import UserService
from bot.handlers.keyboard import KeyBoard
from bot.core.exceptions import KeyAlreadyReceived, KeyTokenNotFound
from bot.utils.generator import generate_invite_link_to_channel
from bot.localization.localizer import localize
from bot.utils.maps import get_days


class GiftHandler:
    def __init__(self, keys_service: KeysService, key_board: KeyBoard, user_service: UserService):
        self._keys_service = keys_service
        self._key_board = key_board
        self._user_service = user_service

    async def handle_gift(self, message: Message, token: str) -> None:
        try:
            key_obj = await self._keys_service.get_key_by_token(token)
        except KeyAlreadyReceived:
            await message.answer('The gift has already been received')
            return
        except KeyTokenNotFound:
            await message.answer('Token not found')
            return

        key = key_obj.key
        user_id = message.from_user.id
        lang = message.from_user.language_code

        text = f'{await localize(lang, "key_text", key)}\n' \
               f'{await localize(lang, "game_text", key_obj.game_name)}\n' \
               f'{await localize(lang, "duration_text", await get_days(lang, key_obj.duration))}'

        await self._keys_service.bind_key_to_user(user_id, key)
        invite_link = await generate_invite_link_to_channel()
        await self._user_service.bind_invite_link(user_id, invite_link)

        await message.answer(
            text=text,
            reply_markup=self._key_board.get_copy_button_with_link(
                text_buttons=(
                    await localize(lang, 'copy_key_btn'),
                    await localize(lang, 'private_channel_btn')
                ),
                text_to_copy=key,
                link=invite_link
            )
        )
