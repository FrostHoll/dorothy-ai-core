from fastapi import FastAPI

from app.api.dependencies import MemoryManagerDep


def register_routes(app: FastAPI, container):

    @app.post("/reset")
    async def reset_history(memory_manager: MemoryManagerDep):
        memory_manager.reset_db()
        return {"message": "DB has been reset."}