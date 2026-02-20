import uuid
from uuid import uuid4

from fastapi import FastAPI

from app.api.dependencies import MemoryManagerDep
from app.api.schemas import GenerateRequest, GenerateResponseSchema, HistoryGetResponse, HistoryGetRequest, \
    ConversationStartResponse


def register_routes(app: FastAPI, container):

    @app.post("/generate", response_model=GenerateResponseSchema)
    async def generate(request: GenerateRequest, memory_manager: MemoryManagerDep):
        use_case = container["generate_response"]
        try:
            convo_id = uuid.UUID(request.conversation_id)
            result = await use_case.execute(request.message, memory_manager, convo_id)
        except ValueError:
            print("Incorrect UUID.")
            result = "Incorrect conversation ID."
        return GenerateResponseSchema(response=result)

    @app.get("/history", response_model=HistoryGetResponse)
    async def get_history(request: HistoryGetRequest, memory_manager: MemoryManagerDep):
        try:
            convo_id = uuid.UUID(request.conversation_id)
            result = await memory_manager.get_recent(convo_id)
        except ValueError:
            print("Incorrect UUID.")
            result = []
        return HistoryGetResponse(messages=result)

    @app.post("/history/reset")
    async def reset_history(memory_manager: MemoryManagerDep):
        memory_manager.reset_db()
        return {"message": "DB has been reset."}

    @app.post("/conversations", response_model=ConversationStartResponse)
    async def start_conversation():
        return ConversationStartResponse(conversation_id=str(uuid4()))