from app.application.generate_response import GenerateResponse
from app.application.memory_manager import MemoryManager
from app.application.persona_manager import PersonaManager
from app.application.prompt_builder import PromptBuilder
from app.domain.interfaces.llm_interface import LLMInterface
from app.infrastructure.llm.async_llama_engine import AsyncLLamaEngine
from app.infrastructure.memory.simple_short_memory import SimpleShortMemory


def create_container():
    llm: LLMInterface = AsyncLLamaEngine()
    memory_manager = MemoryManager(repository=SimpleShortMemory())
    persona_manager = PersonaManager()
    prompt_builder = PromptBuilder(persona_manager, memory_manager)
    generate_response = GenerateResponse(llm, memory_manager, prompt_builder)

    return {
        "generate_response": generate_response,
        "memory_manager": memory_manager
    }