import uuid

from fastapi import APIRouter, File, UploadFile, Form
from starlette.exceptions import HTTPException

from stt_service.api.schemas import JobResponse, JobStatus
from stt_service.core.queue import get_queue
from stt_service.core.store import Job, save_job, get_job


def register_routes() -> APIRouter:
    router = APIRouter(prefix="/api", tags=["api"])

    @router.post(path="/transcribe", response_model=JobResponse)
    async def transcribe(
            audio_file: UploadFile = File(...),
            user_name: str = Form(...)
    ):
        job_id = str(uuid.uuid4())
        audio_bytes: bytes = await audio_file.read()

        job = Job(
            job_id=job_id,
            audio_bytes=audio_bytes,
            filename=audio_file.filename or "audio",
            user_name=user_name
        )
        save_job(job)
        await get_queue().put(job_id)
        return JobResponse(job_id=job_id, status=JobStatus.pending)

    @router.get(path="/get/{job_id}")
    async def get_result(job_id: str):
        job = get_job(job_id)
        if job is None:
            raise HTTPException(status_code=404, detail="Job not found")

        return JobResponse(
            job_id=job.job_id,
            status=job.status,
            text=job.text,
            error=job.error
        )


    return router