from sqlalchemy import String, Integer, BigInteger
from sqlalchemy.orm import Mapped, mapped_column
from bot.database.base import Base
from bot.enums.keys import KeyStatus


class Keys(Base):
    __tablename__ = 'Keys'

    owner_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    key: Mapped[str] = mapped_column(String, nullable=False)
    duration: Mapped[int] = mapped_column(Integer, nullable=False)
    game_name: Mapped[str] = mapped_column(String, nullable=False)
    token: Mapped[str] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, default=KeyStatus.AVAILABLE.value)
