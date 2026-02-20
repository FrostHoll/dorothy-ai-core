from abc import ABC, abstractmethod

from app.domain.entities.message import Message


class LLMInterface(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    async def create_chat_completion(self, messages: list[Message]) -> tuple[Message, str, int]:
        pass

    @abstractmethod
    async def create_restore_completion(self, user_input: str):
        pass

    @abstractmethod
    async def create_summarization_completion(self, user_input: str):
        pass

    @abstractmethod
    def count_tokens(self, text: str) -> int:
        pass

    @abstractmethod
    def get_context_window(self) -> int:
        pass

    @abstractmethod
    def get_reserved_tokens(self) -> int:
        pass