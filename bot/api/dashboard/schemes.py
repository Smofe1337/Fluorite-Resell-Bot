from pydantic import BaseModel
# from typing import Optional

class Auth(BaseModel):
    username: str
    password: str
    # token: Optional[str] = None


class OAuth2(BaseModel):
    token: str
