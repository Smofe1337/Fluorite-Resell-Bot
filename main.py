from aiogram import Dispatcher
from bot.handlers.register import register
from bot.database.init_db import init_db
from bot.api.app import app
from config import Config
import asyncio
import uvicorn
import logging
import sys
import os


def create_directories() -> None:
    paths = [
        Config.UPLOADED_ORDERS_PATH, 
        Config.UPLOADED_IMAGES_PATH
    ]

    for path in paths:
        if not os.path.exists(path):
            print(f'Folder {path} not found. Creating...')
            try:
                os.makedirs(path)
                print(f'Folder {path} successfully created')
            except Exception as e:
                print(f'Failed to create folder {path}: {e}')
                sys.exit(1)
    

async def main():
    create_directories()
    await init_db()

    config = uvicorn.Config(app, host='127.0.0.1', port=1337, reload=True)
    server = uvicorn.Server(config)
    asyncio.create_task(server.serve())

    dp = Dispatcher()
    register(dp)

    from bot.services.init_services import bot
    await dp.start_polling(bot)



if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Shutdown complete')
