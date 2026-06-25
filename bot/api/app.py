from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from bot.services.init_services import container
from config import Config

from bot.api.dashboard.oauth2.security import SecurityManager
from bot.api.dashboard.authorization import AuthRouter
from bot.api.games.management import GamesRouter
from bot.api.keys.management import KeysRouter
from bot.api.users.management import UsersRouter, AvatarRouter
from bot.api.orders.management import OrdersRouter
from bot.api.payments.hooks.aaio import AaioHookRouter
from bot.api.payments.hooks.nicepay import NicepayHookRouter
from bot.api.payments.hooks.cryptobot import CryptobotHookRouter
from bot.api.uploads.management import UploadsRouter


app = FastAPI()
app.mount('/api/static/images', StaticFiles(directory=Config.UPLOADED_IMAGES_PATH), name='images')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:8000', 'http://192.168.1.70:8000', 'http://127.0.0.1:8000'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

security_manager = SecurityManager(container.staff_service)

auth_router = AuthRouter(container.staff_service, security_manager)
games_router = GamesRouter(container.game_service)
keys_router = KeysRouter(container.keys_service)
users_router = UsersRouter(container.user_service, container.bot)
avatar_router = AvatarRouter(container.bot)
orders_router = OrdersRouter(container.order_service, container.user_service, container.crypto_bot, container.bot)
aaio_router = AaioHookRouter(container.order_service, container.user_service, container.bot, container.key_board, container.keys_service, container.aaio)
nicepay_router = NicepayHookRouter(container.order_service, container.user_service, container.keys_service, container.key_board, container.bot)
cryptobot_hook_router = CryptobotHookRouter(container.order_service, container.user_service, container.keys_service, container.key_board, container.bot, container.crypto_bot)
uploads_router = UploadsRouter()

app.include_router(router=uploads_router.router, prefix='/api', tags=['Uploads'])
app.include_router(router=games_router.router, prefix='/api', tags=['Games'])
app.include_router(router=keys_router.router, prefix='/api', tags=['Keys'])
app.include_router(router=nicepay_router.router, prefix='/api', tags=['Payments'])
app.include_router(router=aaio_router.router, prefix='/api', tags=['Payments'])
app.include_router(router=cryptobot_hook_router.router, prefix='/api', tags=['Payments'])
app.include_router(router=users_router.router, prefix='/api', tags=['Users'])
app.include_router(router=avatar_router.router, prefix='/api', tags=['Users'])
app.include_router(router=orders_router.router, prefix='/api', tags=['Orders'])
app.include_router(router=auth_router.router, prefix='/api/dashboard', tags=['Dashboard'])
