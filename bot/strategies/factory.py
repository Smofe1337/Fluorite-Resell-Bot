from bot.services.init_services import key_coupon_strategy, money_coupon_strategy
from bot.enums.coupons import CouponTypes

def get_strategy(coupon_type: str):
    if coupon_type == CouponTypes.KEY.value:
        return key_coupon_strategy
    elif coupon_type == CouponTypes.MONEY.value:
        return money_coupon_strategy
    else:
        raise ValueError()
