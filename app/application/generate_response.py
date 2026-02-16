from app.application.memory_manager import MemoryManager
from app.domain.entities.message import Message
from app.domain.entities.persona import Persona
from app.domain.interfaces.llm_interface import LLMInterface


class GenerateResponse:
    def __init__(self, llm: LLMInterface, memory: MemoryManager, persona: Persona):
        self.llm = llm
        self.memory = memory
        self.persona = persona

    async def execute(self, user_input: str) -> str:
        history = self.memory.get_recent()

        messages = self.build_messages(
            self.persona.system_prompt,
            history,
            user_input
        )

        msg, response, _ = await self.llm.create_chat_completion(messages)

        self.memory.save(msg)

        return response

    def build_messages(self, system_prompt: str, history: list[Message], user_input: str) -> list[Message]:
        return [Message("user", system_prompt), *history, Message("user", user_input)]