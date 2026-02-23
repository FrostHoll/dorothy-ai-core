from typing import Literal

from pydantic import BaseModel


class Message(BaseModel):
    role: Literal["assistant", "user", "system"]
    content: str
    token_count: int = 0