from app.domain.entities.message import Message
from app.domain.interfaces.memory_repository import MemoryRepository


class SimpleShortMemory(MemoryRepository):
    def __init__(self):
        self.memory: list[Message] = []

    def get_short_memories(self) -> list[Message]:
        return self.memory

    def add_memory(self, message: Message):
        self.memory.append(message)