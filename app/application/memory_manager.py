from uuid import UUID

from app.domain.entities.message import Message
from app.domain.interfaces.memory_repository import MemoryRepository


class MemoryManager:
    def __init__(self, repository: MemoryRepository):
        self.repository = repository

    async def get_recent(self, conversation_id: UUID) -> list[Message]:
        return await self.repository.get_recent(conversation_id)

    async def get_context_window(self, conversation_id: UUID, token_budget: int) -> list[Message]:
        messages = await self.repository.get_recent(conversation_id)
        result = []
        total_tokens = 0
        for msg in reversed(messages):
            if total_tokens + msg.token_count <= token_budget:
                result.append(msg)
            else:
                break
        result.reverse()
        return result

    async def save(self, message: Message, conversation_id: UUID):
        await self.repository.add_memory(message, conversation_id)

    async def save_many(self, messages: list[Message], conversation_id: UUID):
        await self.repository.add_many_memory(messages, conversation_id)

    async def reset_db(self):
        await self.repository.reset_db()

    async def get_conversations(self) -> list[str]:
        return await self.repository.get_conversations()

    async def delete_conversation(self, conversation_id: UUID) -> None:
        await self.repository.delete_conversation(conversation_id)

    async def delete_all_conversations(self) -> None:
        await self.repository.delete_all_conversations()