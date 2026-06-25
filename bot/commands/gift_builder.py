from aiogram.types import Message
from bot.database.service.keys import KeysService
from bot.database.service.orders import OrdersService
from bot.enums.orders import OrderType
from bot.utils.generator import get_random_string
from bot.localization.localizer import localize
from bot.views.error_message import send_error_message
from bot.services.init_services import key_board
from config import Config


async def build_gift_link(
        message: Message, 
        key_service: KeysService, 
        order_service: OrdersService,
        user_id: int,
        game_name: str,
        duration: int,
        order_id: str,
        sum: float
    ):
    lang = message.from_user.language_code
    token = get_random_string()
    key = await key_service.get_key(game_name, duration)

    if key:
        link = Config.BOT_BASE_URL + f'?start=gift_{token}'
        
        await message.edit_text(
            text=await localize(lang, 'success_payment_gift_text', link),
            reply_markup=key_board.get_copy_button(
                text_btn=await localize(lang, 'copy_link_btn'),
                text_to_copy=link
            )
        )
        
        await order_service.on_success(
            key_service,
            user_id,
            order_id,
            sum,
            OrderType.GIFT.value,
            key.key,
            token
        )
    else:
        # ERROR CODE #07
        await send_error_message(message, '#07', lang)
