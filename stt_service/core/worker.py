import asyncio
import wave
import numpy as np
from faster_whisper import WhisperModel

from stt_service.api.schemas import JobStatus
from stt_service.core.queue import get_queue
from stt_service.core.store import get_job

_model = WhisperModel(
    model_size_or_path=""
)

async def transcription_worker() -> None:
    queue = get_queue()
    loop = asyncio.get_event_loop()

    while True:
        job_id: str = await queue.get()
        job = get_job(job_id)
        print(f"got job: {job.job_id}")
        if job is None:
            queue.task_done()
            continue

        job.status = JobStatus.processing
        print("processing job...")
        try:
            result = await loop.run_in_executor(
                None,
                _transcribe,
                job.audio_bytes
            )
            job.text = f"{job.user_name}: {result}"
            job.status = JobStatus.done
            with wave.open(f"E://test_{job.user_name}.wav", "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(16000)
                wf.writeframes(job.audio_bytes)
        except Exception as e:
            job.error = str(e)
            job.status = JobStatus.failed
        finally:
            queue.task_done()

def _transcribe(audio_bytes: bytes) -> str | None:
    audio = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32)
    audio_16k = audio / 32768.0
    ## TODO: faster-whisper implementation
    result = _model.transcribe(audio=audio_16k, language="ru")
    print(f"job is done: {result['text']}")
    return result['text']
