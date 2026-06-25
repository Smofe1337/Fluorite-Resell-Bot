from pydantic import BaseModel


class InlineButton(BaseModel):
    text: str
    url: str


class BroadcastRequest(BaseModel):
    text: str
    photos: list[str] = []
    buttons: list[InlineButton] = []
