import uuid

from app.application.memory_manager import MemoryManager
from app.application.persona_manager import PersonaManager
from app.domain.entities.message import Message


class PromptBuilder:
    def __init__(self, persona: PersonaManager):
        self.persona_manager = persona

    async def build(self, user_message: Message, memory_manager: MemoryManager, conversation_id: uuid.UUID, token_budget: int) -> list[Message]:
        persona_prompt = Message(role="system", content=self.persona_manager.get_persona().system_prompt)
        history = await memory_manager.get_context_window(conversation_id, token_budget)
        return [persona_prompt, *history, user_message]