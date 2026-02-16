from app.application.generate_response import GenerateResponse
from app.application.memory_manager import MemoryManager
from app.domain.entities.persona import Persona
from app.domain.interfaces.llm_interface import LLMInterface
from app.infrastructure.llm.async_llama_engine import AsyncLLamaEngine
from app.infrastructure.memory.simple_short_memory import SimpleShortMemory


def create_container():
    llm: LLMInterface = AsyncLLamaEngine()
    memory = MemoryManager(repository=SimpleShortMemory())
    persona: Persona = Persona("Дороти", "ИНСТРУКЦИЯ: Ты девушка, и тебя зовут Дороти. НЕ используй в ответах emoji. НЕ описывай в ответах эмоции или действия.")

    generate_response = GenerateResponse(llm, memory, persona)

    return {
        "generate_response": generate_response
    }