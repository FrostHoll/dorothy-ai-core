from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from voice_orchestrator.api.routers.voice import register_routes as register_voice_routes

app = FastAPI(
    title="Dorothy Voice Orchestrator",
    version="0.1"
)

origins = [
    "http://localhost:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(register_voice_routes())

@app.get("/health")
def root():
    return {"message": "Dorothy Voice Orchestrator is running."}