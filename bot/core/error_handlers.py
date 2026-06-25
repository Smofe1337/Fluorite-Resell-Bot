from functools import wraps
from fastapi import HTTPException, status
from bot.core.exceptions import (
    GameExists,
    KeyExists,
    KeyNotFound,
    GameNotFound,
    UserNotFound,
    InvalidOperator,
    IpAddressAlreadyExists,
    InvalidPassword,
    OrderNotFound,
)


def hook_exceptions(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except GameExists:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail={'Status': False, 'Message': 'Game already exists'})
        except GameNotFound:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={'Status': False, 'Message': 'Game not found'})
        except KeyExists:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail={'Status': False, 'Message': 'Key already exists'})
        except KeyNotFound:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={'Status': False, 'Message': 'Key not found'})
        except UserNotFound:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={'Status': False, 'Message': 'User not found'})
        except InvalidOperator:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={'Status': False, 'Message': 'Invalid operator! Available only - [+ this +=, - this -=] '})
        except IpAddressAlreadyExists:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail={'Status': False, 'Message': 'We have detected potential activity'})
        except InvalidPassword:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={'Status': False, 'Message': 'Invalid Password'})
        except OrderNotFound:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Order not found')
    return wrapper


hook_exeptions = hook_exceptions
