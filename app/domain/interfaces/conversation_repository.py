from abc import ABC, abstractmethod
from typing import Optional
from datetime import datetime

from app.domain.entities.conversation import Conversation


class ConversationRepository(ABC):
    @abstractmethod
    async def add(self, conversation: Conversation) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get(self, conversation_id: str) -> Optional[Conversation]:
        raise NotImplementedError

    @abstractmethod
    async def get_all(self) -> list[Conversation]:
        raise NotImplementedError

    @abstractmethod
    async def update_last_info(self, conversation_id: str, last_user_message: str, last_updated_at: datetime) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update_title(self, conversation_id: str, new_title: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, conversation_id: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete_all(self) -> None:
        raise NotImplementedError