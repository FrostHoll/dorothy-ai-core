from abc import ABC, abstractmethod

from app.domain.interfaces.conversation_repository import ConversationRepository
from app.domain.interfaces.message_repository import MessageRepository


class AbstractUnitOfWork(ABC):
    messages: MessageRepository
    conversations: ConversationRepository

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, *args):
        if exc_type:
            await self.rollback()
        else:
            await self.commit()

    @abstractmethod
    async def commit(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def rollback(self) -> None:
        raise NotImplementedError