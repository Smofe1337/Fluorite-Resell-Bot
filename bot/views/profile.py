from aiogram.types import Message
from datetime import datetime
from bot.services.init_services import user_service
from bot.core.exceptions import UserNotFound
from bot.localization.localizer import localize
from bot.utils.converters import get_usd_price


async def send_user_profile(message: Message):
    user_id = message.from_user.id
    lang = message.from_user.language_code

    try:
        user = await user_service.get_user(user_id)
    except UserNotFound:
        await user_service.register_user(user_id, lang)
        user = await user_service.get_user(user_id)

    if lang == 'ru':
        usd_price = await get_usd_price()
        usd_to_rub = usd_price['rub']

        total_spent = user.total_spent * usd_to_rub
        balance = user.balance * usd_to_rub
    else:
        total_spent = user.total_spent
        balance = user.balance

    return f'{await localize(lang, 'user_id_prof', user_id)}\n' \
           f'{await localize(lang, 'user_balance_prof', round(balance, 2))}\n' \
           f'{await localize(lang, 'total_order_prof', user.total_order)}\n' \
           f'{await localize(lang, 'total_spent_prof', round(total_spent, 2))}\n' \
           f'{await localize(
               lang, 
               'register_at_prof', 
               datetime.fromisoformat(str(user.register_at)).strftime('%d-%m-%Y %H:%M')
            )}\n' \
            f'{await localize(lang, "is_vip_yes_prof" if user.is_vip else "is_vip_no_prof")}\n'
