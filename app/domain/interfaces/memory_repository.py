from abc import ABC, abstractmethod

from app.domain.entities.message import Message


class MemoryRepository(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def get_short_memories(self) -> list[Message]:
        pass

    @abstractmethod
    def add_memory(self, message: Message):
        pass