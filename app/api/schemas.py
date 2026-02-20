from pydantic import BaseModel

from app.domain.entities.message import Message


class GenerateRequest(BaseModel):
    conversation_id: str
    message: str

class GenerateResponseSchema(BaseModel):
    response: str

class HistoryGetRequest(BaseModel):
    conversation_id: str

class HistoryGetResponse(BaseModel):
    messages: list[Message]

class ConversationStartResponse(BaseModel):
    conversation_id: str