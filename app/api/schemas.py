from pydantic import BaseModel
from datetime import datetime
from app.domain.entities.conversation import Conversation
from app.domain.entities.message import Message


class ChatRequest(BaseModel):
    conversation_id: str
    message: str

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    created_at: datetime

class ConversationGetResponse(BaseModel):
    messages: list[Message]

class ConversationStartResponse(BaseModel):
    conversation_id: str

class ConversationsGetAllResponse(BaseModel):
    conversations: list[Conversation]