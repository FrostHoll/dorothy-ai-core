from voice_orchestrator.http_clients.core_client import CoreClient
from voice_orchestrator.http_clients.stt_client import STTClient
from voice_orchestrator.http_clients.tts_client import TTSClient
from voice_orchestrator.voice.voice_segment import VoiceSegment
from voice_orchestrator.voice.voice_session_manager import VoiceSessionManager
from voice_orchestrator.voice.voice_session_state import VoiceSessionState


class VoiceProcessUseCase:
    def __init__(self, voice_session_manager: VoiceSessionManager):
        self.manager = voice_session_manager

    async def execute(self, pcm: bytes, voice_session_id: str, external_id: str, user_id: int, user_name: str) -> None:
        segment = VoiceSegment(user_id, user_name, pcm)
        await self.manager.add_segment(voice_session_id, external_id, segment)

class PollResultUseCase:
    def __init__(self, voice_session_manager: VoiceSessionManager):
        self.manager = voice_session_manager

    async def execute(self, session_id: str) -> tuple[str, bytes | None]:
        if session_id not in self.manager.sessions:
            return "not found", None

        session = self.manager.sessions[session_id]
        if session.state != VoiceSessionState.DONE:
            return "processing", None

        return "done", session.result

class GetVoiceSessionResultsUseCase:
    def __init__(self, voice_session_manager: VoiceSessionManager):
        self.manager = voice_session_manager

    async def execute(self, voice_session_id: str) -> tuple[str, str] | None:
        if voice_session_id not in self.manager.sessions:
            return None
        session = self.manager.sessions[voice_session_id]
        return "\n".join(session.messages), session.response

class CheckModulesStatusUseCase:
    def __init__(self, stt_client: STTClient, core_client: CoreClient, tts_client: TTSClient):
        self.stt = stt_client
        self.core = core_client
        self.tts = tts_client

    async def execute(self) -> tuple[bool, str]:
        has_error = False
        error_msg = ""
        if not await self.stt.check_health():
            has_error = True
            error_msg = " ".join("Модуль STT недоступен.")
        if not await self.core.check_health():
            has_error = True
            error_msg = " ".join("Модуль Core недоступен.")
        if not await self.tts.check_health():
            has_error = True
            error_msg = " ".join("Модуль TTS недоступен.")
        return has_error, error_msg