from pydantic import BaseModel

class Pricing(BaseModel):
    day: int
    week: int
    month: int


class CreateGame(BaseModel):
    game_name: str
    pricing: Pricing
    image_url: str = ''
    status: str
    is_need_show_img: bool


class UpdateStatus(BaseModel):
    game_name: str
    new_status: str


class UpdateImage(BaseModel):
    game_name: str
    image_url: str


class Delete(BaseModel):
    game_name: str


class UpdateGame(BaseModel):
    updating_game: str
    name: str
    pricing: Pricing
    image_url: str
    status: str


class UpdateGameVisibility(BaseModel):
    updating_game: str
    status: bool
