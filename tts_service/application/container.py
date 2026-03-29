from dataclasses import dataclass

from tts_service.application.tts_use_cases import SynthesizeUseCase
from tts_service.core.silero_engine import SileroEngine


@dataclass(frozen=True)
class Container:
    synthesize: SynthesizeUseCase

def create_container() -> Container:
    tts_engine = SileroEngine()

    return Container(
        synthesize=SynthesizeUseCase(tts_engine)
    )