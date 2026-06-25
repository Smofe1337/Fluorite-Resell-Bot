from enum import Enum

class OrderStatus(Enum):
    PAID = 'Paid'
    PENDING = 'Pending'
    EXPIRED = 'Expired'
    CANCELLED = 'Cancelled'
    ERROR = 'Error'


class OrderType(Enum):
    TOP_UP_BALANCE = 'Top up balance'
    KEY = 'Key'
    GIFT = 'Gift'
    UNBAN = 'Unban'
