import uuid

from app.application.memory_manager import MemoryManager
from app.application.prompt_builder import PromptBuilder
from app.domain.entities.message import Message
from app.domain.interfaces.llm_interface import LLMInterface


class GenerateResponse:
    def __init__(self, llm: LLMInterface, prompt_builder: PromptBuilder):
        self.llm = llm
        self.prompt_builder = prompt_builder

    async def execute(self, user_input: str, memory_manager: MemoryManager, conversation_id: uuid.UUID) -> str:
        user_input_tokens = self.llm.count_tokens(user_input)
        token_budget = self.llm.get_context_window() - self.llm.get_reserved_tokens() - user_input_tokens
        user_message = Message(role="user", content=user_input, token_count=user_input_tokens)
        messages = await self.prompt_builder.build(user_message, memory_manager, conversation_id, token_budget)
        msg, response, _ = await self.llm.create_chat_completion(messages)

        await memory_manager.save_many([
            user_message,
            msg
        ], conversation_id)

        return response