from typing import Optional

import httpx

from discord_service.config import settings

class CoreClient:
    def __init__(self):
        self.base_url = settings.core_client_base_url
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=240.0,
            follow_redirects=True
        )

    async def health_check(self) -> bool:
        try:
            response = await self.client.get("/health")
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"[CoreClient]: Error: {str(e)}")
            return False

    async def generate_response(self, user_input: str, external_id: str) -> Optional[str]:
        if not await self.health_check():
            return None
        try:
            payload = {
                "platform": "discord",
                "external_id": external_id,
                "message": user_input
            }
            response = await self.client.post("/chat", json=payload)
            response.raise_for_status()
            reply = response.json()['response']
            return reply
        except Exception as e:
            print(f"[CoreClient]: Error: {str(e)}")
            return None