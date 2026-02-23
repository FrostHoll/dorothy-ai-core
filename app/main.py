from fastapi import FastAPI

from app.api.routes import register_routes
from app.core.container import create_container
from app.api.routers.chat import register_routes as register_chat_routes
from app.api.routers.conversations import register_routes as register_conversations_routes

app = FastAPI()
container = create_container()

register_routes(app, container)
app.include_router(register_chat_routes(container))
app.include_router(register_conversations_routes(container))

@app.get("/")
def root():
    return {"message": "Dorothy Core is running."}