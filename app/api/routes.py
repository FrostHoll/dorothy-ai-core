from fastapi import FastAPI

from app.api.schemas import GenerateRequest, GenerateResponseSchema, HistoryGetResponse


def register_routes(app: FastAPI, container):

    @app.post("/generate", response_model=GenerateResponseSchema)
    async def generate(request: GenerateRequest):
        use_case = container["generate_response"]
        result = await use_case.execute(request.message)
        return GenerateResponseSchema(response=result)

    @app.get("/history", response_model=HistoryGetResponse)
    async def get_history():
        use_case = container["memory_manager"]
        result = use_case.get_recent()
        return HistoryGetResponse(messages=result)