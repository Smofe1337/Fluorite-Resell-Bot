import uuid
import os
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from bot.api.dashboard.oauth2.security import get_current_user
from config import Config


class UploadsRouter:
    def __init__(self):
        self.router = APIRouter(dependencies=[Depends(get_current_user)])
        self._register_routes()

    def _register_routes(self):
        self.router.post('/upload/image/')(self._upload_image)
        self.router.delete('/upload/image/{filename}')(self._delete_image)

    async def _upload_image(self, file: UploadFile = File(...)):
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in Config.ALLOWED_IMAGE_EXTENSIONS:
            raise HTTPException(400, f'Invalid file type. Allowed: {", ".join(Config.ALLOWED_IMAGE_EXTENSIONS)}')

        content = await file.read()
        if len(content) > Config.MAX_IMAGE_SIZE:
            raise HTTPException(400, 'File too large. Max 5MB')

        filename = f'{uuid.uuid4().hex}{ext}'
        path = os.path.join(Config.UPLOADED_IMAGES_PATH, filename)

        with open(path, 'wb') as f:
            f.write(content)

        return {'url': f'{Config.API_BASE_URL}/api/static/images/{filename}'}

    async def _delete_image(self, filename: str):
        path = os.path.join(Config.UPLOADED_IMAGES_PATH, filename)
        if os.path.exists(path):
            os.remove(path)
        return {'status': 'ok'}
