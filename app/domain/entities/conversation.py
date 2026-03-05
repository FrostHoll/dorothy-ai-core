from datetime import datetime
from pydantic import BaseModel


class Conversation(BaseModel):
    id: str
    platform: str
    external_id: str
    title: str = "New chat"
    last_user_message: str | None
    last_updated_at: datetime | None