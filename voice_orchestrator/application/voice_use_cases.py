from discord_service.main import core_client
from voice_orchestrator.http_clients.core_client import CoreClient


class VoiceProcessUseCase:
    def __init__(self, llm_client: CoreClient):
        self.core_client = llm_client

    async def execute(self):
        if not core_client.health_check():
            return None

        # save audio

        # call STT

        # call LLM

        # call TTS
        pass