from typing import Optional

import httpx

from discord_service.config import settings


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

    async def request_response(self, wav_data: bytes, external_id: str) -> Optional[str]:
        if not await self.health_check():
            return None
        try:
            files = {
                "audio_file": ("voice.wav", wav_data, 'audio/wav')
            }
            payload = {
                "external_id": external_id,
                "voice_session_id": 1234
            }
            response = await self.client.post("/voice/process", files=files, json=payload)
            response.raise_for_status()
            return "OK"
        except Exception as e:
            print(f"[CoreClient]: Error: {str(e)}")
            return None