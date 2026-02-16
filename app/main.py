from fastapi import FastAPI

from app.api.routes import register_routes
from app.core.container import create_container

app = FastAPI()
container = create_container()

register_routes(app, container)

@app.get("/")
def root():
    return {"message": "Dorothy Core is running."}