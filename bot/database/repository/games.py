import logging
from sqlalchemy import select, update, delete
from bot.database.models.games import Games
from bot.database.repository.base import BaseRepository
from bot.core.exceptions import GameExists, GameNotFound
from bot.enums.games import GameStatus
from bot.api.games.schemes import Pricing
from typing import Dict, List

logger = logging.getLogger(__name__)


class GamesRepository(BaseRepository):

    async def add_new_game(
            self,
            game_name: str,
            price_day: int,
            price_week: int,
            price_month: int,
            image_url: str,
            status: str,
            is_need_show_img: bool,
    ):
        if await self.is_game_exists(game_name):
            raise GameExists()

        async with self._session() as session:
            new_game = Games(
                name=game_name,
                price_day=price_day,
                price_week=price_week,
                price_month=price_month,
                image_url=image_url,
                status=status,
                is_need_show_img=is_need_show_img,
            )
            session.add(new_game)
            await session.commit()
            return new_game.orm_to_dict()

    async def is_game_exists(self, game_name: str) -> bool:
        async with self._session() as session:
            result = await session.execute(select(Games).where(Games.name == game_name))
            return result.scalars().first() is not None

    async def get_games(self) -> list:
        async with self._session() as session:
            result = await session.execute(select(Games.name).where(Games.status == GameStatus.SAFE.value))
            return result.scalars().all()

    async def get_game_prices(
            self,
            game_name: str,
            target_currency: str,
            exchange_rate: dict,
    ) -> Dict[str, Dict[str, int]]:
        if not await self.is_game_exists(game_name):
            raise GameNotFound()

        async with self._session() as session:
            result = await session.execute(select(Games).where(Games.name == game_name))
            game = result.scalars().first()

            base_prices = {
                'price_day': game.price_day,
                'price_week': game.price_week,
                'price_month': game.price_month,
            }

            if target_currency == game.base_currency:
                return {target_currency: base_prices}

            rate = exchange_rate.get(target_currency)
            converted_prices = {
                key: int(price * rate) for key, price in base_prices.items()
            }

            return {
                target_currency: converted_prices,
                'USD': base_prices,
            }

    async def update_status(self, game_name: str, status: str):
        if not await self.is_game_exists(game_name):
            raise GameNotFound()

        async with self._session() as session:
            await session.execute(update(Games).where(Games.name == game_name).values(status=status))
            await session.commit()

    async def update_image(self, game_name: str, new_image: str):
        if not await self.is_game_exists(game_name):
            raise GameNotFound()

        async with self._session() as session:
            await session.execute(update(Games).where(Games.name == game_name).values(image_url=new_image))
            await session.commit()

    async def get_game(self, game_name: str) -> Games:
        if not await self.is_game_exists(game_name):
            raise GameNotFound()

        async with self._session() as session:
            result = await session.execute(select(Games).where(Games.name == game_name))
            return result.scalars().first()

    async def get_all_games(self) -> List[Dict]:
        async with self._session() as session:
            result = await session.execute(select(Games))
            return [
                {
                    'id': game.id,
                    'name': game.name,
                    'status': game.status,
                    'screenshot': game.image_url,
                    'is_need_show_img': game.is_need_show_img,
                    'pricing': {
                        'oneDay': game.price_day,
                        'sevenDays': game.price_week,
                        'thirtyOneDays': game.price_month,
                    },
                }
                for game in result.scalars().all()
            ]

    async def delete(self, game_name: str):
        async with self._session() as session:
            await session.execute(delete(Games).where(Games.name == game_name))
            await session.commit()

    async def update_game(
            self,
            updating_game: str,
            new_name: str,
            pricing: Pricing,
            image_url: str,
            status: str,
    ):
        if not await self.is_game_exists(updating_game):
            raise GameNotFound()

        async with self._session() as session:
            await session.execute(
                update(Games).where(Games.name == updating_game).values(
                    name=new_name,
                    price_day=pricing.day,
                    price_week=pricing.week,
                    price_month=pricing.month,
                    image_url=image_url,
                    status=status,
                )
            )
            await session.commit()

    async def update_visibility(self, game_name: str, status: bool):
        if not await self.is_game_exists(game_name):
            raise GameNotFound()

        async with self._session() as session:
            await session.execute(update(Games).where(Games.name == game_name).values(is_need_show_img=status))
            await session.commit()
