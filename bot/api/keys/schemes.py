from pydantic import BaseModel
from typing import Literal


class NewKey(BaseModel):
    keys: list[str]
    game_name: str
    duration: int


class DeleteKey(BaseModel):
    key: str


class UpdateKeyStatus(BaseModel):
    key: str
    status: Literal['Available', 'Sold', 'Pending', 'Received']
