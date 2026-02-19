from app.application.memory_manager import MemoryManager
from app.application.persona_manager import PersonaManager
from app.domain.entities.message import Message


class PromptBuilder:
    def __init__(self, persona: PersonaManager, memory: MemoryManager):
        self.persona_manager = persona
        self.memory_manager = memory

    def build(self, user_input: str) -> list[Message]:
        persona_prompt = Message(role="system", content=self.persona_manager.get_persona().system_prompt)
        history = self.memory_manager.get_recent()
        user_prompt = Message(role="user", content=user_input)
        return [persona_prompt, *history, user_prompt]