from aiogram import Bot
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types.copy_text_button import CopyTextButton
from aiogram.exceptions import TelegramForbiddenError
from aiogram.fsm.context import FSMContext
from bot.database.service.users import UserService
from bot.database.service.keys import KeysService
from bot.database.service.orders import OrdersService
from bot.handlers.keyboard import KeyBoard
from bot.core.exceptions import UserNotFound, UserAlreadyExists
from bot.views.welcome_sender import send_welcome
from bot.localization.localizer import localize
from bot.utils.converters import convert_from_usd
from bot.utils.maps import get_currency_by_lang
from bot.utils.logger import Logger
from bot.utils.generator import get_order_id
from bot.enums.telegram_effect import TelegramEffects
from bot.enums.orders import OrderType
from bot.external.fluorite_api import FluoriteApi
from bot.payments.cryptobot import CryptoBot
from bot.security.referral_guard import ReferralGuard, generate_captcha
from bot.state.user import UserState
from config import Config
from datetime import timedelta
from bot.utils.timezone import get_now
import random
import logging

logger = logging.getLogger(__name__)

REFERRAL_MILESTONE = 10


def _get_bonus_range(total_referrals: int) -> tuple[int, int]:
    next_milestone = (total_referrals // REFERRAL_MILESTONE) + 1
    min_bonus = 1 + (next_milestone - 1)
    max_bonus = 5 + 2 * (next_milestone - 1)
    return min_bonus, max_bonus


def _build_progress_bar(current: int, total: int, length: int = 10) -> tuple[str, int]:
    percent = min(int((current / total) * 100), 100) if total > 0 else 0
    filled = int(length * current / total) if total > 0 else 0
    bar = '▓' * filled + '░' * (length - filled)
    return bar, percent


class ReferralHandler:
    def __init__(self, user_service: UserService, keys_service: KeysService,
                 order_service: OrdersService, key_board: KeyBoard, bot: Bot,
                 fluorite_api: FluoriteApi, crypto_bot: CryptoBot,
                 referral_guard: ReferralGuard, bot_logger: Logger):
        self._user_service = user_service
        self._keys_service = keys_service
        self._order_service = order_service
        self._key_board = key_board
        self._bot = bot
        self._fluorite_api = fluorite_api
        self._crypto_bot = crypto_bot
        self._guard = referral_guard
        self._logger = bot_logger

    async def send_referral_info(self, callback: CallbackQuery) -> None:
        user_id = callback.from_user.id
        lang = callback.from_user.language_code
        message = callback.message

        total_referrals = await self._user_service.get_referral_count(user_id)
        referral_link = Config.BOT_BASE_URL + f'?start=ref_{user_id}'

        progress_in_cycle = total_referrals % REFERRAL_MILESTONE
        remaining = REFERRAL_MILESTONE - progress_in_cycle
        bar, percent = _build_progress_bar(progress_in_cycle, REFERRAL_MILESTONE)

        currency = get_currency_by_lang(lang)
        min_usd, max_usd = _get_bonus_range(total_referrals)
        min_bonus = round(await convert_from_usd(currency, min_usd), 2)
        max_bonus = round(await convert_from_usd(currency, max_usd), 2)

        text = await localize(lang, 'referral_title')
        text += '\n' + await localize(lang, 'referral_stats', total_referrals)
        text += '\n' + await localize(lang, 'referral_progress', remaining)
        text += '\n' + await localize(lang, 'referral_progress_bar', bar, percent)
        text += '\n\n' + await localize(lang, 'referral_reward_info', min_bonus, max_bonus)
        text += '\n' + await localize(lang, 'referral_link_label', referral_link)

        copy_btn = InlineKeyboardButton(
            text=await localize(lang, 'referral_copy_btn'),
            copy_text=CopyTextButton(text=referral_link)
        )
        share_btn = InlineKeyboardButton(
            text=await localize(lang, 'referral_share_btn'),
            url=f'https://t.me/share/url?url={referral_link}'
        )
        how_btn = InlineKeyboardButton(
            text=await localize(lang, 'referral_how_btn'),
            callback_data='referral_how'
        )
        back_btn = InlineKeyboardButton(
            text=await localize(lang, 'back_btn'),
            callback_data='back_to_profile'
        )

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [copy_btn, share_btn],
            [how_btn],
            [back_btn]
        ])

        await message.edit_text(text=text, reply_markup=keyboard)

    async def send_how_it_works(self, callback: CallbackQuery) -> None:
        lang = callback.from_user.language_code
        message = callback.message

        text = await localize(lang, 'referral_how_text')

        back_btn = InlineKeyboardButton(
            text=await localize(lang, 'referral_back_to_ref_btn'),
            callback_data='referral_system'
        )

        keyboard = InlineKeyboardMarkup(inline_keyboard=[[back_btn]])
        await message.edit_text(text=text, reply_markup=keyboard)

    async def handle_referral(self, message: Message, inviter_user_id: str, state: FSMContext) -> None:
        if not inviter_user_id.isdigit():
            return

        inviter_user_id = int(inviter_user_id)
        referral_user_id = message.from_user.id
        lang = message.from_user.language_code

        if inviter_user_id == referral_user_id:
            await message.answer(
                text=await localize(lang, 'cant_invite_youself_text')
            )
            return

        try:
            if await self._user_service.is_banned(inviter_user_id):
                await self._user_service.register_user(referral_user_id, lang)
                await send_welcome(message)
                return
        except UserNotFound:
            await self._user_service.register_user(referral_user_id, lang)
            await send_welcome(message)
            return

        status = self._guard.check(inviter_user_id)

        if status == 'attack':
            await self._handle_attack(inviter_user_id, message)
            return

        if status == 'captcha':
            await self._send_captcha(message, inviter_user_id, state)
            return

        await self._complete_referral(message, inviter_user_id, referral_user_id, lang)

    async def handle_captcha_answer(self, message: Message, state: FSMContext) -> None:
        user_id = message.from_user.id
        lang = message.from_user.language_code
        answer_text = message.text

        if not answer_text or not answer_text.lstrip('-').isdigit():
            return

        user_answer = int(answer_text)
        result = self._guard.verify_captcha(user_id, user_answer)

        if result == 'expired':
            await state.clear()
            await message.answer(text=await localize(lang, 'captcha_expired_text'))
            return

        if result == 'wrong':
            state_data = await state.get_data()
            expression = state_data.get('captcha_expression', '?')
            await message.answer(text=await localize(lang, 'captcha_wrong_text', expression))
            return

        await state.clear()
        await message.answer(text=await localize(lang, 'captcha_success_text'))

        state_data = await state.get_data()
        inviter_id = state_data.get('captcha_inviter_id')

        if inviter_id:
            await self._complete_referral(message, inviter_id, user_id, lang)

    async def _send_captcha(self, message: Message, inviter_id: int, state: FSMContext) -> None:
        user_id = message.from_user.id
        lang = message.from_user.language_code

        expression, answer = generate_captcha()
        self._guard.set_captcha(user_id, inviter_id, answer)

        await state.set_state(UserState.waiting_captcha)
        await state.update_data(
            captcha_inviter_id=inviter_id,
            captcha_expression=expression,
        )

        await message.answer(text=await localize(lang, 'captcha_text', expression))
        await self._logger.send_log(
            inviter_id,
            '⚠️ Referral rate limit triggered — captcha sent',
            new_user=user_id,
        )

    async def _handle_attack(self, inviter_id: int, message: Message) -> None:
        pending_users = self._guard.cleanup_inviter(inviter_id)

        if pending_users:
            await self._user_service.delete_users_batch(pending_users)
            await self._user_service.decrement_referral_count(inviter_id, len(pending_users))

        owner_keys = await self._keys_service.get_all_keys_by_user(inviter_id)
        if owner_keys:
            await self._fluorite_api.ban_keys(owner_keys)

        await self._user_service.set_user_ban_status(inviter_id, True)

        try:
            inviter_lang = await self._user_service.get_lang(inviter_id)
            currency = get_currency_by_lang(inviter_lang)
            unban_amount = round(await convert_from_usd(currency, Config.UNBAN_PRICE_USD), 2)
            symbol = '₽' if inviter_lang == 'ru' else '$'

            invoice = await self._crypto_bot.create_invoice(unban_amount, currency)

            if invoice:
                invoice_id, pay_url = invoice

                order_id = get_order_id()
                time_now = get_now(inviter_lang)
                order_expired = time_now + timedelta(minutes=25)

                await self._order_service.new_order({
                    'user_id': inviter_id,
                    'order_id': order_id,
                    'sum': Config.UNBAN_PRICE_USD,
                    'payment_system_order_id': str(invoice_id),
                    'payment_method': 'CryptoBot',
                    'order_type': OrderType.UNBAN.value,
                    'pay_url': pay_url,
                    'expired_at': order_expired.replace(tzinfo=None, microsecond=0),
                })

                ban_text = await localize(
                    inviter_lang, 'referral_attack_ban_text', f'{unban_amount}{symbol}'
                )

                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(
                        text=await localize(inviter_lang, 'referral_unban_pay_btn'),
                        url=pay_url
                    )]
                ])

                await self._bot.send_message(
                    chat_id=inviter_id, text=ban_text, reply_markup=keyboard
                )
            else:
                await self._bot.send_message(
                    chat_id=inviter_id,
                    text=await localize(
                        inviter_lang, 'referral_attack_ban_text', f'{unban_amount}{symbol}'
                    ),
                )
        except (TelegramForbiddenError, UserNotFound):
            pass

        await self._logger.send_log(
            inviter_id,
            '🚨 REFERRAL ATTACK DETECTED — user banned, keys blocked',
            pending_cleaned=len(pending_users),
            keys_banned=len(owner_keys) if owner_keys else 0,
        )

        referral_user_id = message.from_user.id
        lang = message.from_user.language_code
        await self._user_service.register_user(referral_user_id, lang)
        await send_welcome(message)

    async def _complete_referral(self, message: Message, inviter_user_id: int,
                                 referral_user_id: int, lang: str) -> None:
        try:
            total_invited = await self._user_service.get_referral_count(inviter_user_id) + 1

            amount_to_balance = 0
            if total_invited % REFERRAL_MILESTONE == 0:
                min_usd, max_usd = _get_bonus_range(total_invited - 1)
                amount_to_balance = random.randint(min_usd, max_usd)

            await self._user_service.on_new_referral(inviter_user_id, referral_user_id, amount_to_balance)
        except UserAlreadyExists:
            await send_welcome(message)
            return

        await self._user_service.register_user(referral_user_id, lang)
        await send_welcome(message)

        inviter = await self._user_service.get_user(inviter_user_id)
        inviter_lang = inviter.lang

        referral_user_link = f'tg://user?id={referral_user_id}'

        if amount_to_balance > 0:
            inviter_currency = get_currency_by_lang(inviter_lang)
            inviter_balance = await self._user_service.get_balance(inviter_user_id)

            message_to_inviter = await localize(
                inviter_lang,
                'new_referral_with_bonus_text',
                referral_user_link,
                message.from_user.full_name,
                total_invited,
                total_invited,
                round(await convert_from_usd(inviter_currency, amount_to_balance), 2),
                round(await convert_from_usd(inviter_currency, inviter_balance), 2)
            )
        else:
            message_to_inviter = await localize(
                inviter_lang,
                'new_referral_text',
                referral_user_link,
                message.from_user.full_name,
                total_invited,
            )

        try:
            await self._bot.send_message(
                chat_id=inviter_user_id, text=message_to_inviter,
                message_effect_id=TelegramEffects.HEART.value
            )
        except TelegramForbiddenError:
            return
