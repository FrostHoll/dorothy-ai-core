from fastapi import FastAPI, HTTPException
from starlette.middleware.cors import CORSMiddleware

from voice_orchestrator.api.dependencies import ContainerDep
from voice_orchestrator.api.routers.voice import register_routes as register_voice_routes
from voice_orchestrator.application.container import create_container

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

@app.on_event("startup")
async def startup():
    app.state.container = create_container()

app.include_router(register_voice_routes())

@app.get("/health")
async def root(container: ContainerDep):
    use_case = container.check_modules
    has_errors, error_msg = await use_case.execute()
    if has_errors:
        raise HTTPException(status_code=500, detail=error_msg)
    return {"message": "Dorothy Voice Orchestrator is running."}