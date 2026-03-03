import aiosqlite

from app.application.unit_of_work import AbstractUnitOfWork
from app.infrastructure.conversations.sqlite_conversation_repository import SQLiteConversationsRepository
from app.infrastructure.memory.sqlite_message_repository import SQLiteMessageRepository


class SQLiteUnitOfWork(AbstractUnitOfWork):
    def __init__(self, db: aiosqlite.Connection):
        self.db = db
        self.messages = SQLiteMessageRepository(db)
        self.conversations = SQLiteConversationsRepository(db)

    async def commit(self) -> None:
        await self.db.commit()

    async def rollback(self) -> None:
        await self.db.rollback()