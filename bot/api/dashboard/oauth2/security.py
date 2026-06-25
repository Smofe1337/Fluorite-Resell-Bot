from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
from jose import jwt, JWTError
from config import Config
from bot.database.service.dashboard.staff import StaffService

security = HTTPBearer()


class SecurityManager:
    def __init__(self, staff_service: StaffService):
        self._staff_service = staff_service

    @staticmethod
    def create_token(data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.now() + timedelta(days=7)
        to_encode.update({'exp': expire})
        return jwt.encode(to_encode, Config.SECRET, algorithm='HS256')

    async def get_current_user(self, credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
        token = credentials.credentials

        try:
            payload = jwt.decode(token, Config.SECRET, algorithms='HS256')
        except JWTError:
            raise HTTPException(status_code=401, detail='Invalid token')

        username = payload.get('username')
        if username is None:
            raise HTTPException(status_code=401, detail='Not found username')

        user = await self._staff_service.get_user(username)
        if user is None:
            raise HTTPException(status_code=404, detail='User not found')

        return username

    async def validate_token(self, token: str) -> str:
        try:
            payload = jwt.decode(token, Config.SECRET, algorithms=['HS256'])
        except JWTError:
            raise HTTPException(status_code=401, detail='Invalid token')

        username = payload.get('username')
        if username is None:
            raise HTTPException(status_code=401, detail='No username in token')

        user = await self._staff_service.get_user(username)
        if user is None:
            raise HTTPException(status_code=404, detail='User not found')

        return username


def create_token(data: dict) -> str:
    return SecurityManager.create_token(data)


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    from bot.services.init_services import container
    return await container.security_manager.get_current_user(credentials)


async def get_current_user_token(token: str) -> str:
    from bot.services.init_services import container
    return await container.security_manager.validate_token(token)
