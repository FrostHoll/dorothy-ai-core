from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from app.application.container import create_container
from app.api.routers.chat import register_routes as register_chat_routes
from app.api.routers.conversations import register_routes as register_conversations_routes
from app.domain.exceptions import DomainException

app = FastAPI(
    title="Dorothy Core API",
    version="0.1"
)

origins = [
    "http://localhost:8000"
]

@app.on_event("startup")
async def startup():
    app.state.container = create_container()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(register_chat_routes())
app.include_router(register_conversations_routes())

@app.exception_handler(DomainException)
async def domain_exception_handler(request: Request, exc: DomainException):
    return JSONResponse(status_code=400, content={"detail": str(exc)})

@app.get("/health")
def root():
    return {"message": "Dorothy Core is running."}