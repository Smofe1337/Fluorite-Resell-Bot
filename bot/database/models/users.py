from sqlalchemy import BigInteger, Integer,String, Float, Boolean, DateTime, text
from sqlalchemy.orm import Mapped, mapped_column
from bot.database.base import Base
from datetime import datetime


class Users(Base):
    __tablename__ = 'Users'

    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    username: Mapped[str] = mapped_column(String, nullable=True)
    first_name: Mapped[str] = mapped_column(String, nullable=True)
    last_name: Mapped[str] = mapped_column(String, nullable=True)
    lang: Mapped[str] = mapped_column(String, nullable=False)
    register_at: Mapped[datetime] = mapped_column(DateTime, server_default=text("date_trunc('minute', now())"))
    balance: Mapped[float] = mapped_column(Float, default=0)
    total_order: Mapped[int] = mapped_column(BigInteger, default=0)
    total_spent: Mapped[float] = mapped_column(Float, default=0)
    total_invited: Mapped[int] = mapped_column(Integer, default=0)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)
    is_vip: Mapped[bool] = mapped_column(Boolean, default=False)
    invite_link: Mapped[str] = mapped_column(String, nullable=True) # this field for channel with updates


class Referrals(Base):
    __tablename__ = 'Referrals'

    inviter_user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    referral_user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    invited_at: Mapped[DateTime] = mapped_column(DateTime, server_default=text("date_trunc('minute', now())"))
