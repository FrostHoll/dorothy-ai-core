from typing import Optional

import httpx

class CoreClient:
    def __init__(self):
        self.client = httpx.AsyncClient(
            base_url="http://localhost:8080",
            timeout=60.0
        )

    async def check_health(self) -> bool:
        try:
            response = await self.client.get("/health")
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"[VoiceOrchestrator]: Error during core checking health: {str(e)}")
            return False

    async def request_response(self, external_id: str, message: str) -> Optional[str]:
        payload = {
            "platform": "discord-voice",
            "external_id": external_id,
            "message": message
        }
        try:
            response = await self.client.post("/chat", json=payload)
            response.raise_for_status()
            return response.json()['response']
        except Exception as e:
            print(f"[VoiceOrchestrator]: Error during core response request: {str(e)}")
            return None