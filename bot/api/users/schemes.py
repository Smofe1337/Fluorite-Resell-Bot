from pydantic import BaseModel
from typing import Literal


class UpdateBalance(BaseModel):
    user_id: int
    amount: float
    operator: Literal['+', '-']


class SetBanStatus(BaseModel):
    user_id: int
    status: bool


class SetVipStatus(BaseModel):
    user_id: int
    status: bool
