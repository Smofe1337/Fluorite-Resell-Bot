from os import getenv
from dotenv import load_dotenv
import base64

load_dotenv()


class Config:
    BOT_TOKEN = getenv('BOT_TOKEN')
    CB_TOKEN = getenv('CRYPTO_BOT')

    BOT_SECRET = base64.urlsafe_b64decode(getenv('BOT_SECRET'))

    BOT_BASE_URL = ''
    AAIO_BASE_URL = 'https://aaio.so/'

    NICEPAY_MERCHANT_ID = getenv('NICEPAY_MERCHANT_ID')
    NICEPAY_SECRET_KEY = getenv('NICEPAY_SECRET_KEY')

    AAIO_MERCHANT_ID = getenv('AAIO_MERCHANT_ID')
    
    AAIO_SECRET_KEY_1 = getenv('AAIO_SECRET_KEY_1')
    AAIO_SECRET_KEY_2 = getenv('AAIO_SECRET_KEY_2')
    
    AAIO_API_KEY = getenv('AAIO_API_KEY')
    
    BASE_URL_CB = 'https://testnet-pay.crypt.bot/api/'
    NICEPAY_PAYMET_URL = 'https://nicepay.io/public/api/payment'

    BASE_URL_FL = 'https://dashboard.fluorite.wtf/api/reseller/'
    
    DATABASE_URL = getenv('DATABASE_URL')

    FLUORITE_API_TOKEN = getenv('FLUORITE_API')

    ADMIN_LINK = 't.me/Smofegod'
    ADMINS_IDS = [7191689788, 7370655243]
    OWNER_ID = 7191689788

    UPDATE_CHANNEL = -1002689624941

    SECRET = getenv('SECRET')

    UPLOADED_ORDERS_PATH = 'bot/uploaded-orders'
    UPLOADED_IMAGES_PATH = 'bot/uploaded-images'

    API_BASE_URL = 'http://127.0.0.1:1337'

    DEFAULT_GAME_IMAGE = 'default.png'

    ALLOWED_IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.webp', '.gif'}
    MAX_IMAGE_SIZE = 5 * 1024 * 1024

    CAPTCHA_WINDOW = 60
    CAPTCHA_THRESHOLD = 5
    ATTACK_WINDOW = 120
    ATTACK_THRESHOLD = 10
    CAPTCHA_TIMEOUT = 60
    UNBAN_PRICE_USD = 100.0
