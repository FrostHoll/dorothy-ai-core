from app.domain.entities.message import Message
from app.domain.interfaces.memory_repository import MemoryRepository


class MemoryManager:
    def __init__(self, repository: MemoryRepository):
        self.repository = repository

    def get_recent(self) -> list[Message]:
        return self.repository.get_short_memories()

    def save(self, message: Message):
        self.repository.add_memory(message)