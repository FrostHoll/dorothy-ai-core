from pydantic import BaseModel

from app.domain.entities.conversation import Conversation
from app.domain.entities.message import Message


class ChatRequest(BaseModel):
    conversation_id: str
    message: str

class ChatResponse(BaseModel):
    response: str

class ConversationGetResponse(BaseModel):
    messages: list[Message]

class ConversationStartResponse(BaseModel):
    conversation_id: str

class ConversationsGetAllResponse(BaseModel):
    conversations: list[Conversation]