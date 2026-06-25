import os
import re
import asyncio
import logging

from fastapi import APIRouter, Depends, HTTPException
from aiogram import Bot
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    FSInputFile,
    InputMediaPhoto,
)
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest, TelegramRetryAfter

from bot.api.broadcast.schemes import BroadcastRequest
from bot.api.dashboard.oauth2.security import get_current_user
from bot.database.service.users import UserService
from config import Config

logger = logging.getLogger(__name__)


def _resolve_photo(url: str):
    filename = url.split('/')[-1]
    local_path = os.path.join(Config.UPLOADED_IMAGES_PATH, filename)
    if os.path.exists(local_path):
        return local_path
    return url


def _make_photo(src: str):
    if os.path.exists(src):
        return FSInputFile(src)
    return src


class BroadcastRouter:
    def __init__(self, user_service: UserService, bot: Bot):
        self._user_service = user_service
        self._bot = bot
        self._state: dict = {}
        self.router = APIRouter(dependencies=[Depends(get_current_user)])
        self._register_routes()

    def _register_routes(self):
        self.router.post('/broadcast/send/')(self._start_broadcast)
        self.router.get('/broadcast/status/')(self._get_status)

    async def _start_broadcast(self, data: BroadcastRequest):
        if self._state.get('running'):
            raise HTTPException(status_code=409, detail='Broadcast already in progress')

        users = await self._user_service.get_all()
        recipients = [u for u in users if not u.get('is_banned', False)]

        self._state = {
            'running': True,
            'total': len(recipients),
            'sent': 0,
            'failed': 0,
            'finished': False,
        }

        asyncio.create_task(self._send_broadcast(recipients, data))

        return {'Status': True, 'Message': 'Broadcast started', 'total': len(recipients)}

    async def _send_broadcast(self, recipients: list, data: BroadcastRequest):
        reply_markup = None
        if data.buttons:
            reply_markup = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text=btn.text, url=btn.url)]
                    for btn in data.buttons
                ]
            )

        photo_sources = [_resolve_photo(url) for url in data.photos]
        text = re.sub(r'\n{3,}', '\n\n', data.text)

        for user in recipients:
            user_id = user.get('user_id')
            try:
                await self._send_to_user(user_id, text, photo_sources, reply_markup)
                self._state['sent'] += 1
            except TelegramRetryAfter as e:
                await asyncio.sleep(e.retry_after)
                try:
                    await self._send_to_user(user_id, text, photo_sources, reply_markup)
                    self._state['sent'] += 1
                except Exception:
                    self._state['failed'] += 1
            except (TelegramForbiddenError, TelegramBadRequest) as e:
                logger.warning(f'Broadcast skipped user {user_id}: {e}')
                self._state['failed'] += 1
            except Exception as e:
                logger.error(f'Broadcast error for user {user_id}: {e}')
                self._state['failed'] += 1

            await asyncio.sleep(0.04)

        self._state['running'] = False
        self._state['finished'] = True

    async def _send_to_user(self, user_id: int, text: str, photo_sources: list[str], reply_markup):
        if len(photo_sources) == 1:
            await self._bot.send_photo(
                chat_id=user_id,
                photo=_make_photo(photo_sources[0]),
                caption=text,
                reply_markup=reply_markup,
            )
        elif not photo_sources:
            await self._bot.send_message(
                chat_id=user_id,
                text=text,
                reply_markup=reply_markup,
            )
        elif not reply_markup:
            media = [InputMediaPhoto(media=_make_photo(photo_sources[0]), caption=text)] + [
                InputMediaPhoto(media=_make_photo(src)) for src in photo_sources[1:]
            ]
            await self._bot.send_media_group(chat_id=user_id, media=media)
        else:
            media = [InputMediaPhoto(media=_make_photo(src)) for src in photo_sources]
            await self._bot.send_media_group(chat_id=user_id, media=media)
            await self._bot.send_message(
                chat_id=user_id,
                text=text,
                reply_markup=reply_markup,
            )

    async def _get_status(self):
        if not self._state:
            return {'running': False, 'finished': False}
        return self._state
