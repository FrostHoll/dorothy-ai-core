from pydantic import BaseModel

class VoiceProcessResponse(BaseModel):
    voice_session_id: str
    transcript: str
    response_text: str
    latency_ms: int
    audio_base64: str
