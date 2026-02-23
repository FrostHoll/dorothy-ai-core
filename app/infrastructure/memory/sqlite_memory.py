import datetime
import aiosqlite
from uuid import UUID

from app.domain.entities.message import Message
from app.domain.interfaces.memory_repository import MemoryRepository


class SQLiteMemory(MemoryRepository):
    def __init__(self, connection: aiosqlite.Connection) -> None:
        self.connection = connection
        self.wal_enabled = False

    async def init_db(self) -> None:
        await self.connection.execute('''
                    DROP TABLE Memory
            ''')
        await self.connection.execute('''
                    CREATE TABLE IF NOT EXISTS Memory (
                    id INTEGER PRIMARY KEY,
                    role TEXT,
                    content TEXT,
                    created_at DATETIME,
                    token_count INTEGER,
                    conversation_id TEXT
                    )
                    ''')
        await self.connection.execute('''
                    CREATE INDEX IF NOT EXISTS idx_id ON Memory (id)
                    ''')
        await self.connection.commit()

    def _map(self, message_obj) -> Message:
        return Message(
            role=message_obj['role'],
            content=message_obj['content'],
            token_count=message_obj['token_count']
        )

    async def enable_wal(self) -> None:
        await self.connection.execute("PRAGMA journal_mode=WAL;")
        await self.connection.commit()
        self.wal_enabled = True

    async def get_recent(self, conversation_id: UUID) -> list[Message]:
        if not self.wal_enabled:
            await self.enable_wal()
        convo_id = str(conversation_id)
        cursor = await self.connection.execute('''
                SELECT role, content, token_count FROM Memory
                WHERE conversation_id = ?
                ORDER BY created_at ASC
                LIMIT 50
        ''', (convo_id,))
        rows = await cursor.fetchall()
        await cursor.close()
        await self.connection.commit()

        return [self._map(row) for row in rows]

    async def add_memory(self, message: Message, conversation_id: UUID) -> None:
        convo_id = str(conversation_id)
        created_at = datetime.datetime.now()

        await self.connection.execute('''
                INSERT INTO Memory (role, content, created_at, token_count, conversation_id)
                VALUES (?, ?, ?, ?, ?)
        ''', (message.role, message.content, created_at, message.token_count, convo_id))
        await self.connection.commit()

    async def add_many_memory(self, messages: list[Message], conversation_id: UUID) -> None:
        convo_id = str(conversation_id)
        created_at = datetime.datetime.now()

        for message in messages:
            await self.connection.execute('''
                INSERT INTO Memory (role, content, created_at, token_count, conversation_id)
                VALUES (?, ?, ?, ?, ?)
            ''', (message.role, message.content, created_at, message.token_count, convo_id))
        await self.connection.commit()

    async def reset_db(self) -> None:
        await self.init_db()

    async def get_conversations(self) -> list[str]:
        cursor = await self.connection.execute('''
            SELECT DISTINCT conversation_id FROM Memory
        ''')
        rows = await cursor.fetchall()
        await cursor.close()
        await self.connection.commit()
        return [row['conversation_id'] for row in rows]

    async def delete_conversation(self, conversation_id: UUID) -> None:
        convo_id = str(conversation_id)

        await self.connection.execute('''
            DELETE FROM Memory WHERE conversation_id = ?
        ''', (convo_id,))
        await self.connection.commit()

    async def delete_all_conversations(self) -> None:
        await self.connection.execute('''
            DELETE FROM Memory
        ''')
        await self.connection.commit()