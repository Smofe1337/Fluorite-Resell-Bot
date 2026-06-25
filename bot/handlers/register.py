from aiogram import Dispatcher

from bot.services.init_services import container

from bot.handlers.referral_system import ReferralHandler
from bot.handlers.gift import GiftHandler
from bot.handlers.orders.cancel import OrderCancelHandler
from bot.handlers.orders.download import OrderDownloadHandler
from bot.handlers.paymethod.cryptobot import CryptobotPaymentHandler
from bot.handlers.paymethod.balance import BalancePaymentHandler
from bot.handlers.paymethod.aaio import AaioPaymentHandler
from bot.handlers.paymethod.nicepay.nicepay import NicepayPaymentHandler
from bot.handlers.coupon_handlers import KeyCouponHandler, MoneyCouponHandler
from bot.handlers.callback import CallbackRouter
from bot.handlers.text import TextRouter
from bot.handlers.channel import ChannelRouter
from bot.handlers.create_coupon import CreateCouponRouter
from bot.handlers.start.argument import StartArgumentHandler
from bot.handlers.fsm.balance.input_sum import BalanceInputRouter
from bot.handlers.fsm.admins.dashboard import DashboardFSMRouter
from bot.handlers.fsm.paymethod.nicepay.input_email import NicepayEmailRouter
from bot.handlers.fsm.security.captcha import CaptchaRouter

from bot.security.referral_guard import ReferralGuard
from bot.security.channel_guard import ChannelGuard

from bot.commands.start.start import router as start_router
from bot.commands.help import router as help_router
from bot.commands.admins.dashboard import router as dashboard_router
from bot.commands.admins.coupon import router as msg_coupone_router
from bot.commands.activate_coupon import router as coupon_command

referral_guard = ReferralGuard()
channel_guard = ChannelGuard()

referral_handler = ReferralHandler(
    container.user_service, container.keys_service, container.order_service,
    container.key_board, container.bot, container.fluorite_api, container.crypto_bot,
    referral_guard, container.logger
)
gift_handler = GiftHandler(container.keys_service, container.key_board, container.user_service)
order_cancel = OrderCancelHandler(container.order_service, container.crypto_bot, container.key_board)
order_download = OrderDownloadHandler(container.user_service, container.order_service)

cryptobot_payment = CryptobotPaymentHandler(
    container.game_service, container.order_service, container.key_board,
    container.keys_service, container.crypto_bot, container.user_service
)
balance_payment = BalancePaymentHandler(
    container.game_service, container.order_service, container.keys_service,
    container.user_service, container.key_board
)
aaio_payment = AaioPaymentHandler(
    container.game_service, container.order_service, container.key_board, container.aaio
)
nicepay_payment = NicepayPaymentHandler(
    container.game_service, container.order_service, container.nicepay, container.key_board
)

start_argument_handler = StartArgumentHandler(
    container.user_service, container.process_games, referral_handler, gift_handler
)

callback_router = CallbackRouter(
    container.user_service, container.order_service, container.process_games,
    container.key_board, container.fluorite_api, container.logger,
    container.base_coupon_strategy, container.key_coupon_strategy,
    cryptobot_payment, balance_payment, aaio_payment,
    referral_handler, order_download, order_cancel
)

text_router = TextRouter(container.key_board, container.user_service)
channel_router = ChannelRouter(
    container.user_service, container.fluorite_api, container.key_board, container.keys_service,
    channel_guard, container.channel_guard_service
)
create_coupon_router = CreateCouponRouter(container.money_coupon_strategy, container.base_coupon_strategy)
balance_input_router = BalanceInputRouter(container.key_board)
dashboard_fsm_router = DashboardFSMRouter(container.staff_service, container.key_board)
nicepay_email_router = NicepayEmailRouter(nicepay_payment)
captcha_router = CaptchaRouter(referral_handler)

key_coupon_handler = KeyCouponHandler(
    container.coupons_service, container.keys_service, container.user_service, container.key_board
)
money_coupon_handler = MoneyCouponHandler(container.coupons_service, container.user_service)


def register(dp: Dispatcher):
    dp.include_router(start_router)
    dp.include_router(callback_router.router)
    dp.include_router(text_router.router)
    dp.include_router(nicepay_email_router.router)
    dp.include_router(captcha_router.router)
    dp.include_router(channel_router.router)
    dp.include_router(balance_input_router.router)
    dp.include_router(help_router)
    dp.include_router(dashboard_router)
    dp.include_router(dashboard_fsm_router.router)
    dp.include_router(msg_coupone_router)
    dp.include_router(coupon_command)
    dp.include_router(create_coupon_router.router)
