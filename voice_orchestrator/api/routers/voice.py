from fastapi import APIRouter, File, UploadFile, Form

from voice_orchestrator.api.dependencies import ContainerDep
from fastapi.responses import Response
import base64


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

    @router.get(path="/poll-result/{voice_session_id}")
    async def poll_result(container: ContainerDep, voice_session_id: str):
        poll_result_use_case = container.poll_result
        response = await poll_result_use_case.execute(voice_session_id)
        if response[0] != "done":
            return {"status": "processing"}
        get_session_results = container.get_session_results
        transcript, llm_response = await get_session_results.execute(voice_session_id)
        return Response(
            content=response[1],
            media_type="audio/wav",
            headers={
                "X-Status": "done",
                "X-Transcript": base64.b64encode(transcript.encode('utf-8')).decode('utf-8'),
                "X-Response-Text": base64.b64encode(llm_response.encode('utf-8')).decode('utf-8')
            }
        )

    return router