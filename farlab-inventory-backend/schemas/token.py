# User access token schema
from pydantic import BaseModel


class Token(BaseModel):
    """Basemodel for token."""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Tokendata basemodel."""
    username: str | None = None
    user_id: int | None = None
