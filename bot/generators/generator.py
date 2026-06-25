from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from config import Config
import hashlib
import os


def is_image_exists(hash: str) -> bool:
    return Path(f'bot/{Config.UPLOADED_IMAGES_PATH}/{hash}.png').exists()


def hash_filename(name: str) -> str:
    filename_bytes = name.encode('UTF-8')
    return hashlib.sha256(filename_bytes).hexdigest()


def get_new_image(name: str) -> str:
    hashed_filename = hash_filename(name)

    if is_image_exists(hashed_filename):
        return f'bot/{Config.UPLOADED_IMAGES_PATH}/{hashed_filename}.png'


    with Image.open('bot/images/welcome.png').convert('RGBA') as im:

        my_draw = ImageDraw.Draw(im)
        my_draw.font = ImageFont.truetype('bot/fonts/HiraginoKakuGothic.ttc', size=70)
        
        x, y = im.size

        name_bbox = my_draw.textbbox((0, 0), name)
        name_w = name_bbox[2] - name_bbox[0]
        name_h = name_bbox[3] - name_bbox[1]
        name_pos = ((x - name_w) / 2 + 35, (y - name_h) / 2 - 27)

        text = 'Welcome to Fluorite Shop'
        text_bbox = my_draw.textbbox((0, 0), text)
        text_w = text_bbox[2] - text_bbox[0]
        text_h = text_bbox[3] - text_bbox[1]
        text_pos = ((x - text_w) / 2 + 50, (y - text_h) / 2 + 40)

        my_draw.text(name_pos, name, fill=(255, 255, 255, 128))
        my_draw.text(text_pos, text, fill=(255, 255, 255, 128))

        path_save = os.path.join(Config.UPLOADED_IMAGES_PATH, f'{hashed_filename}.png')
        im.save(path_save)

        return path_save

