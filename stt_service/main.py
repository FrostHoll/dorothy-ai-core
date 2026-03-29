import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from stt_service.api.routes import register_routes
from stt_service.core.worker import transcription_worker


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(transcription_worker())
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

app = FastAPI(
    title="Dorothy Speech-To-Text Service",
    version="0.1",
    lifespan=lifespan
)

origins = [
    "http://localhost:8081"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(register_routes())

@app.get("/health")
def root():
    return {"message": "Dorothy Speech-To-Text Service is running."}