import logging
from time import time
from aiogram import Router
from aiogram.types import ChatJoinRequest, ChatMemberUpdated
from aiogram.enums import ChatMemberStatus
from aiogram.exceptions import TelegramForbiddenError
from bot.database.service.users import UserService
from bot.database.service.keys import KeysService
from bot.database.service.channel_guard import ChannelGuardService
from bot.security.channel_guard import ChannelGuard
from bot.handlers.keyboard import KeyBoard
from bot.external.fluorite_api import FluoriteApi
from bot.localization.localizer import localize
from bot.core.exceptions import UserNotFound
from config import Config

logger = logging.getLogger(__name__)


class ChannelRouter:
    def __init__(
        self,
        user_service: UserService,
        fluorite_api: FluoriteApi,
        key_board: KeyBoard,
        keys_service: KeysService,
        channel_guard: ChannelGuard,
        channel_guard_service: ChannelGuardService,
    ):
        self._user_service = user_service
        self._fluorite_api = fluorite_api
        self._key_board = key_board
        self._keys_service = keys_service
        self._guard = channel_guard
        self._guard_service = channel_guard_service
        self.router = Router()
        self._register_routes()

    def _register_routes(self):
        self.router.chat_join_request()(self._on_join_request)
        self.router.chat_member()(self._on_chat_member)

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

    async def _on_chat_member(self, event: ChatMemberUpdated) -> None:
        if event.chat.id != Config.MAIN_CHANNEL:
            return

        old_status: str = event.old_chat_member.status
        new_status: str = event.new_chat_member.status

        joined: bool = (
            new_status == ChatMemberStatus.MEMBER
            and old_status in (ChatMemberStatus.LEFT, ChatMemberStatus.KICKED)
        )
        if not joined:
            return

        user = event.new_chat_member.user
        user_id: int = user.id

        if user_id in Config.ADMINS_IDS:
            return
        try:
            db_user = await self._user_service.get_user(user_id)
            if db_user.is_banned:
                await self._ban(event, user_id, 0, 'blacklisted', self._guard.is_raid())
                return
            if db_user.is_vip or db_user.total_order > 0:
                return
        except UserNotFound:
            pass

        if not self._guard.is_primed():
            since: float = time() - Config.CHANNEL_RATE_WINDOW
            self._guard.prime(await self._guard_service.get_recent_ts(since))

        if self._guard.register_id(user_id):
            await self._ban(event, user_id, 0, 'id_cluster', self._guard.is_raid())
            return

        metrics: dict = self._guard.register_join()
        raid: bool = metrics['is_spike'] or metrics['raid_mode']

        has_photo: bool = await self._has_photo(event, user_id)
        score, reasons = self._guard.score_account(user, has_photo)
        reason: str = ','.join(reasons) or 'clean'

        if raid:
            if score < Config.CHANNEL_MIN_SCORE:
                await self._ban(event, user_id, score, f'raid:{reason}', True)
                return
        else:
            if score == 0:
                await self._ban(event, user_id, score, f'empty:{reason}', False)
                return

        await self._guard_service.log(user_id, score, 'allow', reason, raid)

    async def _has_photo(self, event: ChatMemberUpdated, user_id: int) -> bool:
        try:
            photos = await event.bot.get_user_profile_photos(user_id, limit=1)
            return photos.total_count > 0
        except Exception:
            return False

    async def _ban(self, event: ChatMemberUpdated, user_id: int, score: int, reason: str, is_raid: bool) -> None:
        try:
            await event.bot.ban_chat_member(chat_id=Config.MAIN_CHANNEL, user_id=user_id)
        except Exception as e:
            logger.error(f'Failed to ban {user_id} from main channel: {e}')
        await self._guard_service.log(user_id, score, 'ban', reason, is_raid)
