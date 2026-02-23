import uuid
from uuid import uuid4

from fastapi import APIRouter

from app.api.dependencies import MemoryManagerDep
from app.api.schemas import ConversationStartResponse, ConversationsGetAllResponse, ConversationGetResponse


def register_routes(container) -> APIRouter:
    router = APIRouter(prefix="/conversations", tags=["conversations"])

    @router.post(path="/", response_model=ConversationStartResponse)
    async def start_conversation():
        return ConversationStartResponse(conversation_id=str(uuid4()))

    @router.get(path="/", response_model=ConversationsGetAllResponse)
    async def get_all_conversations(memory_manager: MemoryManagerDep):
        conversations = await memory_manager.get_conversations()
        return ConversationsGetAllResponse(conversations=conversations)

    @router.get(path="/{conversation_id}/messages", response_model=ConversationGetResponse)
    async def get_conversation(conversation_id: str, memory_manager: MemoryManagerDep):
        try:
            convo_id = uuid.UUID(conversation_id)
            result = await memory_manager.get_recent(convo_id)
        except ValueError:
            print("Incorrect UUID.")
            result = []
        return ConversationGetResponse(messages=result)

    @router.get(path="/{conversation_id}/window", response_model=ConversationGetResponse)
    async def get_sliding_window_preview(conversation_id: str, memory_manager: MemoryManagerDep):
        use_case = container['generate_response']
        try:
            convo_id = uuid.UUID(conversation_id)
            result = await use_case.preview_window(memory_manager, convo_id)
        except ValueError:
            print("Incorrect UUID.")
            result = []
        return ConversationGetResponse(messages=result)

    @router.delete(path="/{conversation_id}")
    async def delete_conversation(conversation_id: str, memory_manager: MemoryManagerDep):
        try:
            convo_id = uuid.UUID(conversation_id)
            await memory_manager.delete_conversation(convo_id)
        except ValueError:
            return "Invalid conversation ID."
        return f"Conversation {conversation_id} has been deleted."

    @router.delete(path="/")
    async def delete_all_conversations(memory_manager: MemoryManagerDep):
        await memory_manager.delete_all_conversations()
        return "All conversations have been deleted."

    return router