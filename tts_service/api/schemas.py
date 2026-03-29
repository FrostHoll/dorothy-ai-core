from pydantic import BaseModel


class SynthesizeRequest(BaseModel):
    voice_session_id: str
    text: str