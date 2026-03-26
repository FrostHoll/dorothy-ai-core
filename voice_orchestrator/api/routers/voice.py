from fastapi import APIRouter, File, UploadFile, Form

from voice_orchestrator.api.dependencies import ContainerDep
from voice_orchestrator.api.schemas import PollResultResponse


def register_routes() -> APIRouter:

    router = APIRouter(prefix="/voice", tags=["voice"])

    @router.post(path="/process")
    async def process(
            container: ContainerDep,
            audio_file: UploadFile = File(...),
            external_id: str = Form(...),
            voice_session_id: str = Form(...),
            user_id: int = Form(...),
            user_name: str = Form(...)
    ):
        try:
            audio = await audio_file.read()

            use_case = container.voice_process

            await use_case.execute(
                pcm=audio,
                voice_session_id=voice_session_id,
                external_id=external_id,
                user_id=user_id,
                user_name=user_name
            )

            return {"status": "queued"}
        except Exception as e:
            print(f"Error: {str(e)}")
            return {"error": str(e)}

    @router.get(path="/poll-result/{voice_session_id}", response_model=PollResultResponse)
    async def poll_result(container: ContainerDep, voice_session_id: str):
        use_case = container.poll_result
        response = await use_case.execute(voice_session_id)
        return PollResultResponse(
            status=response[0],
            result=response[1]
        )

    return router