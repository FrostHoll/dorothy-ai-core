import httpx


class TTSClient:
    def __init__(self):
        self.client = httpx.AsyncClient(
            base_url="http://localhost:8083",
            timeout=60.0
        )

    async def check_health(self) -> bool:
        try:
            response = await self.client.get("/health")
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"[VoiceOrchestrator]: Error during TTS checking health: {str(e)}")
            return False

    async def synthesize(self, voice_session_id: str, text: str) -> bytes | None:
        try:
            payload = {
                "voice_session_id": voice_session_id,
                "text": text
            }
            response = await self.client.post("/api/synthesize", json=payload)
            response.raise_for_status()
            wav_bytes = response.content
            return wav_bytes
        except Exception as e:
            print(f"[VoiceOrchestrator]: Error during TTS synthesizing: {str(e)}")
            return None