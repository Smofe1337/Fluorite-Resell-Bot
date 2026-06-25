from sqlalchemy import BigInteger, String, Integer, Boolean, Float, DateTime, text
from sqlalchemy.orm import Mapped, mapped_column
from bot.database.base import Base
from bot.enums.orders import OrderStatus
from datetime import datetime


class Orders(Base):
    __tablename__ = 'Orders'

    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    order_id: Mapped[str] = mapped_column(String, nullable=False)
    game_name: Mapped[str] = mapped_column(String, nullable=True)
    duration: Mapped[int] = mapped_column(Integer, nullable=True)
    sum: Mapped[float] = mapped_column(Float, nullable=False)
    payment_system_order_id: Mapped[str] = mapped_column(String, nullable=False)
    pay_url: Mapped[str] = mapped_column(String, nullable=False)
    order_type: Mapped[str] = mapped_column(String, nullable=False)
    payment_method: Mapped[str] = mapped_column(String, nullable=False)
    create_at: Mapped[datetime] = mapped_column(DateTime, server_default=text("date_trunc('minute', now())"))
    expired_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[str] = mapped_column(String, default=OrderStatus.PENDING.value)
    is_gift: Mapped[bool] = mapped_column(Boolean, nullable=True)
    is_need_back_button: Mapped[bool] = mapped_column(Boolean, nullable=True)
    product: Mapped[str] = mapped_column(String, nullable=True)
