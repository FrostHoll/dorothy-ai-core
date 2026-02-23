from datetime import datetime

class MessageDAO:
    id: int
    role: str
    content: str
    created_at: datetime
    token_count: int
    conversation_id: str