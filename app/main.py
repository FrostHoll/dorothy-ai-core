from fastapi import FastAPI, Request
from starlette.responses import JSONResponse

from app.application.container import create_container
from app.api.routers.chat import register_routes as register_chat_routes
from app.api.routers.conversations import register_routes as register_conversations_routes
from app.domain.exceptions import DomainException

app = FastAPI()

@app.on_event("startup")
async def startup():
    app.state.container = create_container()

app.include_router(register_chat_routes())
app.include_router(register_conversations_routes())

@app.exception_handler(DomainException)
async def domain_exception_handler(request: Request, exc: DomainException):
    return JSONResponse(status_code=400, content={"detail": str(exc)})

@app.get("/")
def root():
    return {"message": "Dorothy Core is running."}