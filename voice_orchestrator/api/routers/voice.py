import wave

from fastapi import APIRouter

from voice_orchestrator.api.schemas import VoiceProcessRequest


def register_routes() -> APIRouter:

    router = APIRouter(prefix="/voice", tags=["voice"])

    @router.post(path="/process")
    async def process(request: VoiceProcessRequest):
        try:
            audio = await request.audio_file.read()

            with wave.open("test.wav", 'wb') as wf:
                wf.setnchannels(2)
                wf.setsampwidth(2)
                wf.setframerate(48000)
                wf.writeframes(audio)
                print("file saved")
        except Exception as e:
            print(f"Error: {str(e)}")

    return router