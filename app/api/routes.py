from fastapi import FastAPI

from app.api.schemas import GenerateRequest, GenerateResponseSchema


def register_routes(app: FastAPI, container):

    @app.post("/generate")
    async def generate(request: GenerateRequest):
        use_case = container["generate_response"]
        result = await use_case.execute(request.message)
        return GenerateResponseSchema(response=result)