from dataclasses import dataclass

from app.application.chat_use_cases import GenerateResponseUseCase, PreviewContextWindowUseCase
from app.application.persona_service import PersonaService
from app.application.prompt_builder import PromptBuilder
from app.domain.interfaces.llm_interface import LLMInterface
from app.infrastructure.llm.async_llama_engine import AsyncLLamaEngine


@dataclass(frozen=True)
class Container:
    generate_response: GenerateResponseUseCase
    preview_context_window: PreviewContextWindowUseCase

def create_container() -> Container:
    llm: LLMInterface = AsyncLLamaEngine()
    persona_manager = PersonaService()
    prompt_builder = PromptBuilder(persona_manager)
    generate_response = GenerateResponseUseCase(llm, prompt_builder)
    preview_context_window = PreviewContextWindowUseCase(llm, prompt_builder)

    return Container(
        generate_response=generate_response,
        preview_context_window=preview_context_window
    )