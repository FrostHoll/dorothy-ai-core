from pydantic import BaseModel


class GenerateRequest(BaseModel):
    message: str

class GenerateResponseSchema(BaseModel):
    response: str
