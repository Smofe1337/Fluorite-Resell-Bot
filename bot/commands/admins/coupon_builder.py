from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from bot.core.exceptions import CouponAlreadyExists
from bot.utils.generator import get_random_string
from bot.services.init_services import coupons_service


async def build_coupone(message: Message, state: FSMContext) -> None:
    data = await state.get_data()

    if data is None:
        await message.answer('Unable to retrieve information about coupon #1')
        return
        
    activation_limit = data['activation_limit']
    max_redemptions_per_user = data['max_redemptions_per_user']
    coupon_type = data['coupon_type']
    vip_flag = data['vip_flag']
    expires_at = data['expires_at']
    amount = data.get('amount')
    game = data.get('game')
    duration = data.get('duration')

    if all([activation_limit, coupon_type, vip_flag, expires_at, max_redemptions_per_user]) is not None:
        coupone_data = {}

        coupon = get_random_string()
        coupone_data['coupon'] = coupon
        coupone_data['coupon_type'] = coupon_type
        coupone_data['activation_limit'] = activation_limit
        coupone_data['max_redemptions_per_user'] = max_redemptions_per_user
        coupone_data['is_vip'] = vip_flag
        coupone_data['expires_at'] = expires_at
        coupone_data['amount'] = amount
        coupone_data['game'] = game
        coupone_data['duration'] = duration

        try:
            await coupons_service.create(coupone_data)
        except CouponAlreadyExists:
            await message.answer('Coupone already exists')
            return
        
        text = '<b>Coupon successfully created!</b>\n' \
        f'Coupon: <code>{coupon}</code>\n' \
        f'Expires at: {expires_at}'

        await message.answer(text=text)
