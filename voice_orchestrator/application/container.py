from dataclasses import dataclass

from voice_orchestrator.application.voice_use_cases import VoiceProcessUseCase, PollResultUseCase
from voice_orchestrator.http_clients.core_client import CoreClient
from voice_orchestrator.http_clients.stt_client import STTClient
from voice_orchestrator.http_clients.tts_client import TTSClient
from voice_orchestrator.voice.voice_session_manager import VoiceSessionManager


@dataclass(frozen=True)
class Container:
    voice_process: VoiceProcessUseCase
    poll_result: PollResultUseCase

def create_container() -> Container:
    stt_client = STTClient()
    core_client = CoreClient()
    tts_client = TTSClient()
    voice_session_manager = VoiceSessionManager(stt_client, core_client, tts_client)

    return Container(
        voice_process=VoiceProcessUseCase(voice_session_manager),
        poll_result=PollResultUseCase(voice_session_manager)
    )