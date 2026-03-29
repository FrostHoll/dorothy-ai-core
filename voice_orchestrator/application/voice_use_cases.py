from voice_orchestrator.voice.voice_segment import VoiceSegment
from voice_orchestrator.voice.voice_session_manager import VoiceSessionManager
from voice_orchestrator.voice.voice_session_state import VoiceSessionState


class VoiceProcessUseCase:
    def __init__(self, voice_session_manager: VoiceSessionManager):
        self.manager = voice_session_manager

    async def execute(self, pcm: bytes, voice_session_id: str, external_id: str, user_id: int, user_name: str):
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