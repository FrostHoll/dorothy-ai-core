import httpx

class STTClient:
    def __init__(self):
        self.client = httpx.AsyncClient(
            base_url="http://localhost:8082",
            timeout=60.0
        )

    async def check_health(self) -> bool:
        try:
            response = await self.client.get("/health")
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"[VoiceOrchestrator]: Error during STT checking health: {str(e)}")
            return False

    async def enqueue_segment(self, audio_bytes: bytes, user_name: str) -> str | None:
        try:
            files = {
                "audio_file": ("voice.wav", audio_bytes, 'audio/wav')
            }
            data = {
                "user_name": user_name
            }
            response = await self.client.post("/api/transcribe", files=files, data=data)
            response.raise_for_status()
            job_id = response.json()['job_id']
            return job_id
        except Exception as e:
            print(f"[VoiceOrchestrator]: Error during STT enqueueing: {str(e)}")
            return None

    async def poll_result(self, job_id: str) -> str | None:
        try:
            response = await self.client.get(f"/api/get/{job_id}")
            response.raise_for_status()
            job_response = response.json()
            if job_response['status'] == "done":
                return job_response['text']
            if job_response['status'] == "failed":
                raise Exception(job_response['error'])
            return None
        except Exception as e:
            print(f"[VoiceOrchestrator]: Error during STT getting: {str(e)}")
            return None