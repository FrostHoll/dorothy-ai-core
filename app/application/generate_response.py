from app.application.memory_manager import MemoryManager
from app.application.prompt_builder import PromptBuilder
from app.domain.entities.message import Message
from app.domain.interfaces.llm_interface import LLMInterface


class GenerateResponse:
    def __init__(self, llm: LLMInterface, memory_manager: MemoryManager, prompt_builder: PromptBuilder):
        self.llm = llm
        self.memory_manager = memory_manager
        self.prompt_builder = prompt_builder

    async def execute(self, user_input: str) -> str:
        messages = self.prompt_builder.build(user_input)
        msg, response, _ = await self.llm.create_chat_completion(messages)

        self.memory_manager.save(Message(role="user", content=user_input))
        self.memory_manager.save(msg)

        return response