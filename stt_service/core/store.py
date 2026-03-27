from dataclasses import dataclass

from stt_service.api.schemas import JobStatus


@dataclass
class Job:
    job_id: str
    audio_bytes: bytes
    filename: str
    user_name: str = "None"
    status: JobStatus = JobStatus.pending
    text: str | None = None
    error: str | None = None

_store: dict[str, Job] = {}

def save_job(job: Job) -> None:
    _store[job.job_id] = job

def get_job(job_id: str) -> Job | None:
    return _store.get(job_id)