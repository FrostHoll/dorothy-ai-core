from fastapi import APIRouter

from app.api.dependencies import ContainerDep, UOWDep
from app.api.schemas import ChatResponse, ChatRequest


def register_routes() -> APIRouter:

    router = APIRouter(prefix="/chat", tags=["chat"])


    @router.post("/", response_model=ChatResponse)
    async def chat(request: ChatRequest, container: ContainerDep, uow: UOWDep):
        use_case = container.generate_response
        use_case.uow = uow
        response, created_at = await use_case.execute(request.message, request.conversation_id)
        return ChatResponse(response=response, conversation_id=request.conversation_id, created_at=created_at)

    return router