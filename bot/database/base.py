from sqlalchemy import Integer
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)


    def orm_to_dict(self, exclude: list[str] = None, skip_none = False) -> dict:
        exclude = exclude or []
        return {
            k: (v.strftime('%Y-%m-%d %H:%M:%S') if hasattr(v, 'isoformat') else v)
            for k, v in vars(self).items()
            if not k.startswith('_') 
            and not callable(v) 
            and k not in exclude 
            and (not skip_none or v is not None)
        }
