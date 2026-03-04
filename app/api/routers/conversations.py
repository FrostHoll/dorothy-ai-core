from uuid import uuid4

from fastapi import APIRouter, HTTPException
from starlette import status

from app.api.dependencies import UOWDep, ContainerDep
from app.api.schemas import ConversationStartResponse, ConversationsGetAllResponse, ConversationGetResponse, \
    ConversationEditTitleRequest
from app.application.message_use_cases import GetAllConversationsUseCase, GetConversationUseCase, \
    DeleteConversationUseCase, DeleteAllConversationsUseCase, EditConversationTitleUseCase
from app.domain.exceptions import TooLongTitleException


def register_routes() -> APIRouter:
    router = APIRouter(prefix="/conversations", tags=["conversations"])

    @router.post(path="/", response_model=ConversationStartResponse)
    async def start_conversation():
        return ConversationStartResponse(conversation_id=str(uuid4()))

    @router.get(path="/", response_model=ConversationsGetAllResponse)
    async def get_all_conversations(uow: UOWDep):
        use_case = GetAllConversationsUseCase(uow)
        conversations = await use_case.execute()
        return ConversationsGetAllResponse(conversations=conversations)

    @router.get(path="/{conversation_id}/messages", response_model=ConversationGetResponse)
    async def get_conversation(conversation_id: str, uow: UOWDep):
        use_case = GetConversationUseCase(uow)
        result = await use_case.execute(conversation_id)
        return ConversationGetResponse(messages=result)

    @router.get(path="/{conversation_id}/window", response_model=ConversationGetResponse)
    async def get_sliding_window_preview(conversation_id: str, container: ContainerDep, uow: UOWDep):
        use_case = container.preview_context_window
        use_case.uow = uow
        result = await use_case.execute(conversation_id)
        return ConversationGetResponse(messages=result)

    @router.delete(path="/{conversation_id}")
    async def delete_conversation(conversation_id: str, uow: UOWDep):
        use_case = DeleteConversationUseCase(uow)
        await use_case.execute(conversation_id)
        return f"Conversation {conversation_id} has been deleted."

    @router.delete(path="/")
    async def delete_all_conversations(uow: UOWDep):
        use_case = DeleteAllConversationsUseCase(uow)
        await use_case.execute()
        return "All conversations have been deleted."

    @router.patch(path="/{conversation_id}")
    async def edit_title(conversation_id: str, request: ConversationEditTitleRequest, uow: UOWDep):
        use_case = EditConversationTitleUseCase(uow)
        try:
            await use_case.execute(conversation_id, request.title)
        except TooLongTitleException as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        return request.title


    return router