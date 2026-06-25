from aiogram.types import Message, CallbackQuery
from typing import Callable, Union
from functools import wraps
from config import Config


def admin_only(handle: Callable):
    @wraps(handle)
    async def wrapper(event: Union[Message, CallbackQuery], *args, **kwargs):
        user_id = event.from_user.id
        if user_id not in Config.ADMINS_IDS:
            return      
        return await handle(event, *args, **kwargs)
    return wrapper
    
