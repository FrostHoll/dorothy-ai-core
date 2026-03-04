from app.application.unit_of_work import AbstractUnitOfWork
from app.domain.entities.conversation import Conversation
from app.domain.entities.message import Message
from app.domain.exceptions import TooLongTitleException


class GetAllConversationsUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    async def execute(self) -> list[Conversation]:
        async with self.uow as uow:
            conversations = await uow.conversations.get_all()
            return conversations

class GetConversationUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    async def execute(self, conversation_id: str) -> list[Message]:
        async with self.uow as uow:
            messages = await uow.messages.get_recent(conversation_id)
            return messages

class DeleteConversationUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    async def execute(self, conversation_id: str) -> None:
        async with self.uow as uow:
            await uow.messages.delete_conversation(conversation_id)
            await uow.conversations.delete(conversation_id)

class DeleteAllConversationsUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    async def execute(self) -> None:
        async with self.uow as uow:
            await uow.messages.delete_all_conversations()
            await uow.conversations.delete_all()

class EditConversationTitleUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    async def execute(self, conversation_id: str, new_title: str) -> None:
        if len(new_title) > 30:
            raise TooLongTitleException(title=new_title)
        async with self.uow as uow:
            await uow.conversations.update_title(conversation_id, new_title)