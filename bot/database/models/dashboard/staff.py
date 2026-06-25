from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from bot.database.base import Base


class Staff(Base):
    __tablename__ = 'Staff'

    username: Mapped[str] = mapped_column(String, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
