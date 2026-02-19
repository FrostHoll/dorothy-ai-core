from pydantic import BaseModel

from app.domain.entities.message import Message


class GenerateRequest(BaseModel):
    message: str

class GenerateResponseSchema(BaseModel):
    response: str

class HistoryGetResponse(BaseModel):
    messages: list[Message]