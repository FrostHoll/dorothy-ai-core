from fastapi import UploadFile
from pydantic import BaseModel

class VoiceProcessRequest(BaseModel):
    audio_file: UploadFile
    external_id: str
    voice_session_id: str

class VoiceProcessResponse(BaseModel):
    voice_session_id: str
    transcript: str
    response_text: str
    latency_ms: int
    audio_base64: str


