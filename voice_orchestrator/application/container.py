from dataclasses import dataclass

from voice_orchestrator.application.voice_use_cases import VoiceProcessUseCase, PollResultUseCase
from voice_orchestrator.voice.voice_session_manager import VoiceSessionManager


@dataclass(frozen=True)
class Container:
    voice_process: VoiceProcessUseCase
    poll_result: PollResultUseCase

def create_container() -> Container:
    voice_session_manager = VoiceSessionManager()

    return Container(
        voice_process=VoiceProcessUseCase(voice_session_manager),
        poll_result=PollResultUseCase(voice_session_manager)
    )