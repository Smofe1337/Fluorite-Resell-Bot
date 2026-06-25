from sqlalchemy import String, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from bot.database.base import Base
from bot.enums.games import GameStatus


class Games(Base):
    __tablename__ = 'Games'

    name: Mapped[str] = mapped_column(String, nullable=False)
    base_currency: Mapped[str] = mapped_column(String, default='USD')
    price_day: Mapped[int] = mapped_column(Integer, nullable=False)
    price_week: Mapped[int] = mapped_column(Integer, nullable=False)
    price_month: Mapped[int] = mapped_column(Integer, nullable=False)
    image_url: Mapped[str] = mapped_column(String, nullable=False)
    is_need_show_img: Mapped[bool] = mapped_column(Boolean)
    status: Mapped[str] = mapped_column(String, default=GameStatus.SAFE.value)
