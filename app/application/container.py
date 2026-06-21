from dataclasses import dataclass

from app.application.chat_use_cases import GenerateResponseUseCase, PreviewContextWindowUseCase
from app.application.persona_service import PersonaService
from app.application.prompt_builder import PromptBuilder
from app.domain.interfaces.llm_interface import LLMInterface
from app.infrastructure.llm.async_llama_engine import AsyncLLamaEngine
from app.infrastructure.tools.classes.GetWebpageTool import GetWebpageTool
from app.infrastructure.tools.classes.ListToolsTool import ListToolsTool
from app.infrastructure.tools.classes.RollNumberTool import RollNumberTool
from app.infrastructure.tools.classes.WebSearchTool import WebSearchTool
from app.infrastructure.tools.text_postprocessor import TextPostprocessor
from app.infrastructure.tools.tool_container import ToolContainer
from app.infrastructure.tools.tool_proxy import ToolProxy


@dataclass(frozen=True)
class Container:
    generate_response: GenerateResponseUseCase
    preview_context_window: PreviewContextWindowUseCase

def create_container() -> Container:
    tool_container = ToolContainer()
    llm: LLMInterface = AsyncLLamaEngine(tool_container)
    persona_manager = PersonaService()
    prompt_builder = PromptBuilder(persona_manager)
    generate_response = GenerateResponseUseCase(llm, prompt_builder)
    preview_context_window = PreviewContextWindowUseCase(llm, prompt_builder)


    TextPostprocessor.tool_container = tool_container
    tool_container.register_tool(ToolProxy(ListToolsTool, tool_container=tool_container), enabled_by_default=True)
    tool_container.register_tool(ToolProxy(WebSearchTool), enabled_by_default=True)
    tool_container.register_tool(ToolProxy(GetWebpageTool), enabled_by_default=True)
    tool_container.register_tool(ToolProxy(RollNumberTool), enabled_by_default=True)

    return Container(
        generate_response=generate_response,
        preview_context_window=preview_context_window
    )