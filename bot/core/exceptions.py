class GameExists(Exception): pass
class GameNotFound(Exception): pass

class KeyExists(Exception): pass
class KeyNotFound(Exception): pass
class KeyAlreadyReceived(Exception): pass
class KeyTokenNotFound(Exception): pass

class FailedParseResponse(Exception): pass
class FailedCreatePayment(Exception): pass

class UserNotFound(Exception): pass
class UserAlreadyExists(Exception): pass

class IpAddressAlreadyExists(Exception): pass

class InvalidOperator(Exception): pass

class InvalidPassword(Exception): pass

class OrderNotFound(Exception): pass

class CouponAlreadyExists(Exception): pass
class CouponNotFound(Exception): pass

class InactiveCouponError(Exception): pass
class CouponRedemptionLimitExceededError(Exception): pass
class NonVipUserError(Exception): pass
class ExpiredCouponError(Exception): pass
class MaxUserRedemptionsExceededError(Exception): pass
