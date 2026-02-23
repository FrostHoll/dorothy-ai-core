from uuid import UUID

from app.domain.entities.message import Message
from app.domain.interfaces.memory_repository import MemoryRepository


class SimpleShortMemory(MemoryRepository):
    def __init__(self):
        self.memory: list[Message] = []

    async def get_recent(self, conversation_id: UUID) -> list[Message]:
        return self.memory

    async def add_memory(self, message: Message, conversation_id: UUID):
        self.memory.append(message)