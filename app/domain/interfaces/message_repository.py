from abc import ABC, abstractmethod

from app.domain.entities.message import Message


class MessageRepository(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    async def get_recent(self, conversation_id: str) -> list[Message]:
        pass

    @abstractmethod
    async def get_context_window(self, conversation_id: str, token_budget: int) -> list[Message]:
        raise NotImplementedError

    @abstractmethod
    async def add_memory(self, message: Message, conversation_id: str):
        pass

    @abstractmethod
    async def add_many_memory(self, messages: list[Message], conversation_id: str):
        pass

    @abstractmethod
    async def get_conversations(self):
        pass

    @abstractmethod
    async def delete_conversation(self, conversation_id: str) -> None:
        pass

    @abstractmethod
    async def delete_all_conversations(self) -> None:
        pass