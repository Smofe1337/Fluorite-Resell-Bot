from aiogram import Router
from aiogram.types import ChatJoinRequest
from aiogram.exceptions import TelegramForbiddenError
from bot.database.service.users import UserService
from bot.database.service.keys import KeysService
from bot.handlers.keyboard import KeyBoard
from bot.external.fluorite_api import FluoriteApi
from bot.localization.localizer import localize
from bot.core.exceptions import UserNotFound
from config import Config


class ChannelRouter:
    def __init__(self, user_service: UserService, fluorite_api: FluoriteApi, key_board: KeyBoard, keys_service: KeysService):
        self._user_service = user_service
        self._fluorite_api = fluorite_api
        self._key_board = key_board
        self._keys_service = keys_service
        self.router = Router()
        self._register_routes()

    def _register_routes(self):
        self.router.chat_join_request()(self._on_join_request)

    async def _on_join_request(self, event: ChatJoinRequest) -> None:
        if event.invite_link.creator.id not in Config.ADMINS_IDS:
            invite_link = event.invite_link.invite_link
            link_owner = await self._user_service.get_user_by_invite_link(invite_link)

            if link_owner:
                link_owner_id = link_owner.user_id
                invite_link = event.invite_link.invite_link
                sender_id = event.from_user.id
                sendr_lang = event.from_user.language_code

                if sender_id != link_owner_id:
                    await self._user_service.set_user_ban_status(link_owner_id, True)

                    try:
                        await self._user_service.set_user_ban_status(sender_id, True)
                    except UserNotFound:
                        await self._user_service.register_user(sender_id, sendr_lang)
                        await self._user_service.set_user_ban_status(sender_id, True)

                    await event.bot.ban_chat_member(chat_id=Config.UPDATE_CHANNEL, user_id=link_owner_id)
                    await event.bot.ban_chat_member(chat_id=Config.UPDATE_CHANNEL, user_id=sender_id)

                    owner_keys = await self._keys_service.get_all_keys_by_user(link_owner_id)
                    owner_info = await self._user_service.get_user_info(link_owner_id)

                    await self._fluorite_api.ban_keys(owner_keys)

                    try:
                        await event.bot.send_message(
                            chat_id=link_owner_id,
                            text=await localize(owner_info['language'], 'you_are_banned_text')
                        )
                    except TelegramForbiddenError:
                        return

                    await event.answer_pm(text=await localize(sendr_lang, 'access_denied_text'))
                else:
                    await event.approve()
            else:
                await event.answer_pm(
                    text=await localize(sendr_lang, 'failed_verif_text', '#07', '#07', sender_id, invite_link),
                    reply_markup=self._key_board.get_copy_button_with_link(
                        text_buttons=(
                            await localize(sendr_lang, 'copy_sample_btn'),
                            await localize(sendr_lang, 'contact_support_btn')
                        ),
                        text_to_copy=await localize(sendr_lang, 'sample_text', '#07', sender_id, invite_link),
                        link=Config.ADMIN_LINK
                    )
                )
