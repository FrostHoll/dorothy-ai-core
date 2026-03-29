from fastapi import APIRouter, HTTPException
from starlette.responses import StreamingResponse

from tts_service.api.dependencies import ContainerDep
from tts_service.api.schemas import SynthesizeRequest


def register_routes() -> APIRouter:
    router = APIRouter(prefix="/api", tags=["api"])

    @router.post(path="/synthesize")
    async def synthesize(container: ContainerDep, request: SynthesizeRequest):
        use_case = container.synthesize

        audio_bytes = await use_case.execute(request.text)
        if audio_bytes is None:
            raise HTTPException(status_code=500, detail="TTS generation failed. (check logs)")

        return StreamingResponse(
            audio_bytes,
            media_type="audio/wav"
        )




    return router