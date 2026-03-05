from fastapi import APIRouter

from app.api.dependencies import ContainerDep, UOWDep
from app.api.schemas import ChatResponse, ChatRequest


def register_routes() -> APIRouter:

    router = APIRouter(prefix="/chat", tags=["chat"])


    @router.post("/", response_model=ChatResponse)
    async def chat(request: ChatRequest, container: ContainerDep, uow: UOWDep):
        use_case = container.generate_response
        use_case.uow = uow
        response, conversation_id, created_at = await use_case.execute(request.message, request.platform, request.external_id)
        return ChatResponse(response=response, conversation_id=conversation_id, created_at=created_at)

    return router