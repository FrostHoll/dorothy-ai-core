from app.application.persona_service import PersonaService
from app.domain.entities.message import Message
from app.domain.interfaces.message_repository import MessageRepository


class PromptBuilder:
    def __init__(self, persona: PersonaService):
        self.persona_manager = persona

    async def build(self, user_message: Message, message_repo: MessageRepository, conversation_id: str, token_budget: int) -> list[Message]:
        persona_prompt = Message(role="system", content=self.persona_manager.get_persona().system_prompt)
        history = await message_repo.get_context_window(conversation_id, token_budget)
        return [persona_prompt, *history, user_message]