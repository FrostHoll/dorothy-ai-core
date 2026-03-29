from enum import Enum

from pydantic import BaseModel


class JobStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    done = "done"
    failed = "failed"

class JobResponse(BaseModel):
    job_id: str
    status: JobStatus
    text: str | None = None
    error: str | None = None