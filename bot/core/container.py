import logging
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config import Config

from bot.database.repository.users import UserRepository
from bot.database.repository.games import GamesRepository
from bot.database.repository.keys import KeysRepository
from bot.database.repository.orders import OrdersRepository
from bot.database.repository.dashboard.staff import StaffRepository
from bot.database.repository.coupons import CouponsRepository
from bot.database.repository.channel_guard import ChannelGuardRepository

from bot.database.service.users import UserService
from bot.database.service.games import GameService
from bot.database.service.keys import KeysService
from bot.database.service.orders import OrdersService
from bot.database.service.dashboard.staff import StaffService
from bot.database.service.coupons import CouponsService
from bot.database.service.channel_guard import ChannelGuardService

from bot.handlers.keyboard import KeyBoard
from bot.handlers.callbacks.process_game import ProcessGames

from bot.external.fluorite_api import FluoriteApi

from bot.payments.cryptobot import CryptoBot
from bot.payments.nicepay import NicePay
from bot.payments.aaio import Aaio

from bot.core.crypto import SecureURLManager
from bot.core.security import PasswordManager

from bot.utils.logger import Logger

from bot.strategies.base import BaseCouponStrategy
from bot.strategies.money_coupon import MoneyCouponStrategy
from bot.strategies.key_coupon import KeyCouponStrategy

from bot.api.dashboard.oauth2.security import SecurityManager

logger = logging.getLogger(__name__)


class ServiceContainer:
    def __init__(self):
        logger.info('Initializing service container')

        self.bot = Bot(
            Config.BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )

        self.password_manager = PasswordManager()
        self.crypto = SecureURLManager(Config.BOT_SECRET)

        self._init_repositories()
        self._init_services()
        self._init_ui()
        self._init_external()
        self._init_strategies()
        self._init_security()

        self.logger = Logger(self.bot)

        logger.info('Service container initialized')

    def _init_repositories(self):
        self.user_repo = UserRepository()
        self.game_repo = GamesRepository()
        self.keys_repo = KeysRepository()
        self.order_repo = OrdersRepository()
        self.staff_repo = StaffRepository(self.password_manager)
        self.coupons_repo = CouponsRepository()
        self.channel_guard_repo = ChannelGuardRepository()

    def _init_services(self):
        self.user_service = UserService(self.user_repo)
        self.keys_service = KeysService(self.keys_repo, self.game_repo)
        self.game_service = GameService(self.game_repo, self.keys_service)
        self.order_service = OrdersService(self.order_repo, self.user_service)
        self.staff_service = StaffService(self.staff_repo)
        self.coupons_service = CouponsService(self.coupons_repo, self.user_service)
        self.channel_guard_service = ChannelGuardService(self.channel_guard_repo)

    def _init_ui(self):
        self.key_board = KeyBoard(self.game_service, self.keys_service)
        self.process_games = ProcessGames(self.game_service, self.key_board)

    def _init_external(self):
        self.fluorite_api = FluoriteApi()
        self.crypto_bot = CryptoBot(Config.CB_TOKEN, Config.BASE_URL_CB)
        self.nicepay = NicePay(Config.NICEPAY_MERCHANT_ID, Config.NICEPAY_SECRET_KEY, Config.NICEPAY_PAYMET_URL)
        self.aaio = Aaio(Config.AAIO_MERCHANT_ID, Config.AAIO_SECRET_KEY_1, Config.AAIO_API_KEY, Config.AAIO_BASE_URL)

    def _init_strategies(self):
        self.base_coupon_strategy = BaseCouponStrategy()
        self.money_coupon_strategy = MoneyCouponStrategy()
        self.key_coupon_strategy = KeyCouponStrategy(self.key_board)

    def _init_security(self):
        self.security_manager = SecurityManager(self.staff_service)
