from typing import Literal
from datetime import datetime
from pydantic import BaseModel


class Message(BaseModel):
    role: Literal["assistant", "user", "system"]
    content: str
    token_count: int = 0
    created_at: datetime = datetime.now()