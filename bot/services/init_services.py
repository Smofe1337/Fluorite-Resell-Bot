import logging
import sys
from bot.core.container import ServiceContainer

_logger = logging.getLogger(__name__)

try:
    container = ServiceContainer()

    bot = container.bot
    password_manager = container.password_manager
    crypto = container.crypto

    user_service = container.user_service
    keys_service = container.keys_service
    game_service = container.game_service
    order_service = container.order_service
    staff_service = container.staff_service
    coupons_service = container.coupons_service

    key_board = container.key_board
    process_games = container.process_games

    fluorite_api = container.fluorite_api
    crypto_bot = container.crypto_bot
    nicepay = container.nicepay
    aaio = container.aaio

    logger = container.logger

    base_coupon_strategy = container.base_coupon_strategy
    money_coupon_strategy = container.money_coupon_strategy
    key_coupon_strategy = container.key_coupon_strategy

    security_manager = container.security_manager

except Exception as e:
    _logger.critical(f'Failed to initialize services: {e}')
    sys.exit(1)
