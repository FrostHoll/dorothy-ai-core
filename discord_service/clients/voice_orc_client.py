from typing import Optional

import httpx

from discord_service.config import settings
from discord_service.voice.audio_data_record import AudioDataRecord


class VoiceOrchestratorClient:
    def __init__(self):
        self.base_url = settings.voice_orchestrator_base_url
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=60.0,
            follow_redirects=True
        )

    async def health_check(self) -> bool:
        try:
            response = await self.client.get("/health")
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"[VoiceOrchestratorClient]: Error: {str(e)}")
            return False

    async def request_process(self, voice_session_id: str, external_id: str, audio_record: AudioDataRecord) -> Optional[str]:
        if not await self.health_check():
            return None
        try:
            files = {
                "audio_file": ("voice.wav", audio_record.build_pcm(), 'audio/wav')
            }
            payload = {
                "external_id": external_id,
                "voice_session_id": voice_session_id,
                "user_id": audio_record.user_id,
                "user_name": audio_record.user_name
            }
            response = await self.client.post("/voice/process", files=files, data=payload)
            response.raise_for_status()
            return "OK"
        except Exception as e:
            print(f"[VoiceOrchestratorClient]: Error: {str(e)}")
            return None

    async def poll_result(self, voice_session_id: str) -> Optional[str]:
        if not await self.health_check():
            return None
        try:
            response = await self.client.get(f"/voice/poll-result/{voice_session_id}")
            response.raise_for_status()
            status: str = response.json()['status']
            result: str | None = None
            if status == "done":
                result = response.json()['result']
            return result
        except Exception as e:
            print(f"[VoiceOrchestratorClient]: Error: {str(e)}")
            return None