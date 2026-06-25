from sqlalchemy import BigInteger, Integer, String, Float, Boolean, DateTime, text
from sqlalchemy.orm import Mapped, mapped_column
from bot.database.base import Base
from datetime import datetime


class ChannelGuardLog(Base):
    __tablename__ = 'ChannelGuardLog'

    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    ts: Mapped[float] = mapped_column(Float, nullable=False)
    joined_at: Mapped[datetime] = mapped_column(DateTime, server_default=text('now()'))
    score: Mapped[int] = mapped_column(Integer, default=0)
    action: Mapped[str] = mapped_column(String, nullable=False)
    reason: Mapped[str] = mapped_column(String, nullable=True)
    is_raid: Mapped[bool] = mapped_column(Boolean, default=False)
