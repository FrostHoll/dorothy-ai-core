import uuid
from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.message import Message


class MemoryRepository(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    async def get_recent(self, conversation_id: UUID) -> list[Message]:
        pass

    @abstractmethod
    async def add_memory(self, message: Message, conversation_id: uuid.UUID):
        pass

    @abstractmethod
    async def add_many_memory(self, messages: list[Message], conversation_id: UUID):
        pass

    @abstractmethod
    async def reset_db(self):
        pass