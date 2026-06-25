from aiogram.types import FSInputFile
from bot.services.init_services import bot
from datetime import datetime, timedelta
from bot.localization.localizer import localize
from bot.generators.generator import get_new_image
from config import Config
import random
import string


def get_order_id() -> str:
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))


def get_random_string() -> str:
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=15))

    
async def generate_order_text(
        lang: str, 
        order_id: str, 
        product: str, 
        pay_method: str,
        amount: float,
        create_at: datetime, 
        pay_before: datetime
    ) -> str:
    return f'{await localize(lang, 'order_id_ord', order_id)}\n' \
           f'{await localize(lang, 'product_ord', product)}\n' \
           f'{await localize(lang, 'amount_ord', amount)}\n' \
           f'{await localize(lang, 'paymethod_ord', pay_method)}\n' \
           f'{await localize(lang, 'created_at_ord', create_at)}\n' \
           f'{await localize(lang, 'pay_before_ord', pay_before)}\n\n' \
           f'{await localize(lang, "user_agreement_ord")}'


async def generate_order_text_balance(
        lang: str, 
        order_id: str, 
        pay_method: str,
        amount: float,
        create_at: datetime, 
        pay_before: datetime
    ) -> str:
    return f'{await localize(lang, 'order_id_ord', order_id)}\n' \
           f'{await localize(lang, 'amount_ord', amount)}\n' \
           f'{await localize(lang, 'paymethod_ord', pay_method)}\n' \
           f'{await localize(lang, 'created_at_ord', create_at)}\n' \
           f'{await localize(lang, 'pay_before_ord', pay_before)}\n\n' \
           f'{await localize(lang, "user_agreement_ord")}'


async def generate_balance_pay(
        lang: str, order_id: str,
        product: str, pay_method: str,
        create_at: datetime
) -> str:
    return f'{await localize(lang, 'order_id_ord', order_id)}\n' \
           f'{await localize(lang, 'product_ord', product)}\n' \
           f'{await localize(lang, 'paymethod_ord', pay_method)}\n' \
           f'{await localize(lang, 'created_at_ord', create_at)}'


async def generate_invite_link_to_channel():
    link = await bot.create_chat_invite_link(
        chat_id=Config.UPDATE_CHANNEL, 
        expire_date=datetime.timestamp(datetime.now() + timedelta(minutes=25)), 
        creates_join_request=True
    )

    return link.invite_link


def random_key() -> str:
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))


async def get_welcome_text(lang: str, first_name: str) -> str:
    return await localize(
        lang,
        'welcome_msg',
        first_name
    )


def get_welcome_photo(first_name: str):
    image = get_new_image(first_name)
    return FSInputFile(image)


def generate_password():
    return ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=10))
