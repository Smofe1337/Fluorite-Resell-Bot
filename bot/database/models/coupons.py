from sqlalchemy import String, Boolean, Integer, BigInteger, Float, DateTime, text
from sqlalchemy.orm import Mapped, mapped_column
from bot.database.base import Base
from datetime import datetime

class Coupons(Base):
    __tablename__ = 'Coupons'
    
    coupone: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    coupon_type: Mapped[str] = mapped_column(String, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=True)
    game: Mapped[str] = mapped_column(String, nullable=True)
    duration: Mapped[int] = mapped_column(Integer, nullable=True)
    activation_limit: Mapped[int] = mapped_column(Integer, nullable=False)
    times_redeemed: Mapped[int] = mapped_column(Integer, default=0)
    max_redemptions_per_user: Mapped[int] = mapped_column(Integer, nullable=False)
    is_vip: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_activate: Mapped[bool] = mapped_column(Boolean, default=True)
    create_at: Mapped[datetime] = mapped_column(DateTime, server_default=text("date_trunc('minute', now())"))
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)


class CouponsUsers(Base):
    __tablename__ = 'Coupons_Users'

    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    coupone: Mapped[str] = mapped_column(String, nullable=False)
    activate_at: Mapped[datetime] = mapped_column(DateTime, server_default=text("date_trunc('minute', now())"))
    redemption_count: Mapped[int] = mapped_column(Integer, default=0)
