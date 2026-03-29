from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from tts_service.api.routes import register_routes
from tts_service.application.container import create_container

app = FastAPI(
    title="Dorothy Text-To-Speech Service",
    version="0.1"
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

@app.on_event("startup")
async def startup():
    app.state.container = create_container()

app.include_router(register_routes())

@app.get("/health")
def root():
    return {"message": "Dorothy Text-To-Speech Service is running."}