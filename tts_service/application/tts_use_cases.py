import io

from tts_service.core.silero_engine import SileroEngine


class SynthesizeUseCase:
    def __init__(self, engine: SileroEngine):
        self.engine = engine

    async def execute(self, text: str) -> io.BytesIO | None:
        buffer = self.engine.synthesize(text)
        return buffer
