from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from bot.core.exceptions import (
    InactiveCouponError,
    CouponRedemptionLimitExceededError,
    NonVipUserError,
    ExpiredCouponError,
    CouponNotFound,
    MaxUserRedemptionsExceededError,
    UserNotFound
)
from bot.enums.coupons import CouponTypes
from bot.localization.localizer import localize
from bot.services.init_services import user_service, coupons_service

router = Router()


@router.message(Command('activate'))
async def activate_coupone_command(message: Message) -> bool:
    user_id = message.from_user.id
    lang = message.from_user.language_code

    try:
        if await user_service.is_banned(user_id):
            return
    except UserNotFound:
        await user_service.register_user(user_id, lang)

    parts = message.text.split()
    if len(parts) <= 1 or not parts[1] or len(parts[1]) > 15:
        await message.answer(
            text=await localize(lang, 'coupone_invalid_text')
        )
        return

    coupon = parts[1]

    try:
        await coupons_service.on_use(coupon, user_id)
    except InactiveCouponError:
        await message.answer(
            text=await localize(lang, 'coupone_inactive_text')
        )
        return
    except CouponRedemptionLimitExceededError:
        await message.answer(
            text=await localize(lang, 'coupon_redemption_limit_exceeded_text')
        )
        return
    except NonVipUserError:
        await message.answer(
            text=await localize(lang, 'non_vip_user_error_text')
        )
        return
    except ExpiredCouponError:
        await message.answer(
            text=await localize(lang, 'expired_coupon_text')
        )
        return
    except CouponNotFound:
        await message.answer(
            text=await localize(lang, 'coupone_not_found_text')
        )
        return
    except MaxUserRedemptionsExceededError:
        await message.answer(
            text=await localize(lang, 'max_user_redemptions_exceeded_text')
        )
        return

    coupon_type = await coupons_service.get_type(coupon)

    from bot.handlers.register import key_coupon_handler, money_coupon_handler

    if coupon_type == CouponTypes.KEY.value:
        await key_coupon_handler.process(message, coupon)
    elif coupon_type == CouponTypes.MONEY.value:
        await money_coupon_handler.process(message, coupon)
