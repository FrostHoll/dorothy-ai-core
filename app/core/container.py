from app.application.generate_response import GenerateResponse
from app.application.persona_manager import PersonaManager
from app.application.prompt_builder import PromptBuilder
from app.domain.interfaces.llm_interface import LLMInterface
from app.infrastructure.llm.async_llama_engine import AsyncLLamaEngine


def create_container():
    llm: LLMInterface = AsyncLLamaEngine()
    persona_manager = PersonaManager()
    prompt_builder = PromptBuilder(persona_manager)
    generate_response = GenerateResponse(llm, prompt_builder)

    return {
        "generate_response": generate_response
    }