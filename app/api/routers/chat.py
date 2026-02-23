import uuid

from fastapi import APIRouter

from app.api.dependencies import MemoryManagerDep
from app.api.schemas import ChatResponse, ChatRequest


def register_routes(container) -> APIRouter:

    router = APIRouter(prefix="/chat", tags=["chat"])


    @router.post("/", response_model=ChatResponse)
    async def chat(request: ChatRequest, memory_manager: MemoryManagerDep):
        use_case = container["generate_response"]
        try:
            convo_id = uuid.UUID(request.conversation_id)
            result = await use_case.execute(request.message, memory_manager, convo_id)
        except ValueError:
            print("Incorrect UUID.")
            result = "Incorrect conversation ID."
        return ChatResponse(response=result)

    return router