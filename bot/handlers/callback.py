from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.handlers.paymethod.cryptobot import CryptobotPaymentHandler
from bot.handlers.paymethod.balance import BalancePaymentHandler
from bot.handlers.paymethod.aaio import AaioPaymentHandler
from bot.handlers.referral_system import ReferralHandler
from bot.handlers.orders.download import OrderDownloadHandler
from bot.handlers.orders.cancel import OrderCancelHandler
from bot.handlers.callbacks.process_game import ProcessGames
from bot.handlers.keyboard import KeyBoard
from bot.database.service.users import UserService
from bot.database.service.orders import OrdersService
from bot.external.fluorite_api import FluoriteApi
from bot.utils.logger import Logger
from bot.strategies.base import BaseCouponStrategy
from bot.strategies.key_coupon import KeyCouponStrategy
from bot.views.game_message import send_game_message
from bot.views.profile import send_user_profile
from bot.localization.localizer import localize
from bot.strategies.factory import get_strategy
from bot.utils.maps import duration_map_int
from bot.state.payments import Payments
from bot.state.user import UserState
from bot.state.admins import CreateCoupon
from bot.core.exceptions import UserNotFound
from bot.enums.orders import OrderStatus


class CallbackRouter:
    def __init__(self, user_service: UserService, order_service: OrdersService, process_games: ProcessGames,
                 key_board: KeyBoard, fluorite_api: FluoriteApi, logger: Logger,
                 base_coupon_strategy: BaseCouponStrategy, key_coupon_strategy: KeyCouponStrategy,
                 cryptobot_payment: CryptobotPaymentHandler, balance_payment: BalancePaymentHandler,
                 aaio_payment: AaioPaymentHandler, referral_handler: ReferralHandler,
                 order_download: OrderDownloadHandler, order_cancel: OrderCancelHandler):
        self._user_service = user_service
        self._order_service = order_service
        self._process_games = process_games
        self._key_board = key_board
        self._fluorite_api = fluorite_api
        self._logger = logger
        self._base_coupon_strategy = base_coupon_strategy
        self._key_coupon_strategy = key_coupon_strategy
        self._cryptobot_payment = cryptobot_payment
        self._balance_payment = balance_payment
        self._aaio_payment = aaio_payment
        self._referral_handler = referral_handler
        self._order_download = order_download
        self._order_cancel = order_cancel
        self.router = Router()
        self._register_routes()

    def _register_routes(self):
        self.router.callback_query()(self._process_callback)

    async def _process_callback(self, callback: CallbackQuery, state: FSMContext):
        user_id = callback.from_user.id
        lang = callback.from_user.language_code

        try:
            if await self._user_service.is_banned(user_id):
                return
        except UserNotFound:
            await self._user_service.register_user(user_id, lang)
            await self._logger.send_log(user_id, 'New user registered')

        data = callback.data
        message = callback.message

        state_data = await state.get_data()
        is_gift = state_data.get('is_gift', False)

        if data.startswith('game_'):
            await message.delete()
            game_name = data.split('_')[1]
            await self._process_games.select_duration(message, game_name, lang)

        elif data.endswith('price_day') or data.endswith('price_week') or data.endswith('price_month'):
            await message.delete()
            splited_data = data.split('_')
            game_name = splited_data[0]
            duration = splited_data[2]
            await state.update_data(game_name=game_name)
            await self._process_games.select_paymethod(message, game_name, duration, lang)

        elif data.endswith('cryptobot'):
            await self._cryptobot_payment.paymethod_cryptobot(callback, data, is_gift)

        elif data.endswith('nicepay'):
            await state.set_state(Payments.request_email)
            await state.update_data(callback_data=data, is_gift=is_gift)
            await message.edit_text(text=await localize(lang, 'send_email_msg'))

        elif data.endswith('aaio'):
            await self._aaio_payment.paymethod_aaio(callback, data, is_gift)

        elif data == 'payment_cryptobot_balance':
            await self._cryptobot_payment.paymethod_cryptobot_balance(callback, state)

        elif data == 'payment_nicepay_balance':
            await state.set_state(Payments.request_email)
            await message.edit_text(text=await localize(lang, 'send_email_msg'))

        elif data == 'payment_aaio_balance':
            await self._aaio_payment.paymethod_aaio_balance(callback, state)

        elif data.endswith('payment_balance'):
            await self._balance_payment.paymethod_balance_create(callback, data, is_gift, state)

        elif data.startswith('pay_via_balance'):
            order_id = data.split(':')[1]
            await self._balance_payment.paymethod_balance(callback, order_id)

        elif data.startswith('reset_hwid'):
            await message.edit_text(
                text=await localize(lang, 'keys_text'),
                reply_markup=await self._key_board.keys_button(user_id, lang=lang)
            )

        elif data.startswith('keys_page:'):
            offset = int(data.split(':')[1])
            await message.edit_text(
                text=await localize(lang, 'keys_text'),
                reply_markup=await self._key_board.keys_button(user_id, offset, lang=lang)
            )

        elif data.startswith('r_hwid'):
            key = data.split(':')[1]
            if await self._fluorite_api.reset_hwid(key):
                await message.edit_text(
                    text=await localize(lang, 'hwid_reset_success_text')
                )
            else:
                await message.edit_text(
                    text=await localize(lang, 'hwid_reset_error_text')
                )

        elif data == 'up_balance':
            await state.set_state(UserState.wait_sum_to_up_balance)
            await state.update_data(is_balance=True)
            await message.edit_text(
                text=await localize(lang, 'input_amount_text')
            )

        elif data == 'top_up_balance':
            await message.edit_text(
                text=await localize(lang, 'select_paymethod_text'),
                reply_markup=self._key_board.get_payment_balance()
            )

        elif data == 'referral_system':
            await self._referral_handler.send_referral_info(callback)

        elif data == 'referral_how':
            await self._referral_handler.send_how_it_works(callback)

        elif data == 'back_to_profile':
            profile_text = await send_user_profile(callback)
            await message.edit_text(
                text=profile_text,
                reply_markup=await self._key_board.get_profile(lang)
            )

        elif data.startswith('back_to_purchases'):
            splited_data = data.split(':')
            splited_data[1] += '_payment_balance'
            is_gift = state_data.get('is_gift_safe')
            await self._balance_payment.paymethod_balance_create(
                callback,
                splited_data[1],
                is_gift,
                state
            )

        elif data == 'download_orders':
            await self._order_download.download_orders(callback)

        elif data.startswith('orders_page:'):
            await self._order_download.handle_page(callback)

        elif data == 'back_to_games':
            await message.delete()
            await send_game_message(message, lang)

        elif data == 'back_to_duration':
            game_name = state_data.get('game_name')
            await message.delete()
            await self._process_games.select_duration(message, game_name, lang)

        elif data == 'back_to_paymethod':
            await message.delete()
            game_name = state_data.get('game_name')
            days = duration_map_int.get(state_data.get('duration_str'))
            await self._process_games.select_paymethod(message, game_name, days, lang)

        elif data.startswith('cancel_order'):
            order_id = data.split(':')[1]
            if order_id is None:
                return

            order_status = await self._order_service.get_status(order_id)
            prohibited_statuses = [OrderStatus.CANCELLED.value, OrderStatus.PAID.value, OrderStatus.EXPIRED.value]

            if order_status in prohibited_statuses:
                await callback.answer(
                    text=await localize(lang, 'order_unavailable_alert'),
                    show_alert=True
                )
                await message.delete()
                return

            await self._order_cancel.confirm_cancel_order(callback, order_id)

        elif data.startswith('order_confirm_yes'):
            order_id = data.split(':')[1]
            if order_id is None:
                return
            await self._order_cancel.delete_order(callback, order_id)

        elif data.startswith('order_confirm_no'):
            order_id = data.split(':')[1]
            if order_id is None:
                return
            await self._order_cancel.back_to_payment(callback, order_id)

        elif data.startswith('sected_coupon_type'):
            coupon_type = data.split(':')[1]
            await state.update_data(coupon_type=coupon_type)
            strategy = get_strategy(coupon_type)
            await message.delete()
            await strategy.start(message, state)

        elif data.startswith('vip_flag:'):
            await self._base_coupon_strategy.handle_vip_flag(callback, state)

        elif data.startswith('selected_game'):
            game = data.split(':')[1]
            await state.update_data(game=game)
            await self._key_coupon_strategy.handle_select_duration(callback, state)

        elif data.startswith('selected_duration'):
            duration = data.split(':')[1]
            await state.update_data(duration=int(duration))
            await self._base_coupon_strategy.handle_vip_flag(callback, state)
            await state.set_state(CreateCoupon.waiting_for_activation_limit)
            await callback.message.delete()
            await callback.message.answer('Enter activation limit')
