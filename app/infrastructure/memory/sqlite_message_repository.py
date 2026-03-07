import datetime
import aiosqlite

from app.domain.entities.message import Message
from app.domain.interfaces.message_repository import MessageRepository


class SQLiteMessageRepository(MessageRepository):
    def __init__(self, connection: aiosqlite.Connection) -> None:
        self.connection = connection

    async def get_recent(self, conversation_id: str) -> list[Message]:
        convo_id = str(conversation_id)
        cursor = await self.connection.execute('''
                SELECT role, content, token_count, created_at FROM Memory
                WHERE conversation_id = ?
                ORDER BY created_at ASC
        ''', (convo_id,))
        rows = await cursor.fetchall()
        await cursor.close()

        return [self._row_to_message(row) for row in rows]

    async def get_context_window(self, conversation_id: str, token_budget: int) -> list[Message]:
        messages = await self.get_recent(conversation_id)
        result = []
        total_tokens = 0
        for msg in reversed(messages):
            if total_tokens + msg.token_count <= token_budget:
                result.append(msg)
                total_tokens += msg.token_count
            else:
                break
        result.reverse()
        return result

    async def add_memory(self, message: Message, conversation_id: str) -> None:
        convo_id = str(conversation_id)
        created_at = datetime.datetime.now()

        await self.connection.execute('''
                INSERT INTO Memory (role, content, created_at, token_count, conversation_id)
                VALUES (?, ?, ?, ?, ?)
        ''', (message.role, message.content, created_at, message.token_count, convo_id))

    async def add_many_memory(self, messages: list[Message], conversation_id: str) -> None:
        convo_id = str(conversation_id)
        created_at = datetime.datetime.now()

        for message in messages:
            await self.connection.execute('''
                INSERT INTO Memory (role, content, created_at, token_count, conversation_id)
                VALUES (?, ?, ?, ?, ?)
            ''', (message.role, message.content, created_at, message.token_count, convo_id))

    async def get_conversations(self) -> list[str]:
        cursor = await self.connection.execute('''
            SELECT DISTINCT conversation_id FROM Memory
        ''')
        rows = await cursor.fetchall()
        await cursor.close()
        return [row['conversation_id'] for row in rows]

    async def delete_conversation(self, conversation_id: str) -> None:
        convo_id = str(conversation_id)

        await self.connection.execute('''
            DELETE FROM Memory WHERE conversation_id = ?
        ''', (convo_id,))

    async def delete_all_conversations(self) -> None:
        await self.connection.execute('''
            DELETE FROM Memory
        ''')

    @staticmethod
    def _row_to_message(message_obj) -> Message:
        return Message(
            role=message_obj['role'],
            content=message_obj['content'],
            token_count=message_obj['token_count'],
            created_at=message_obj['created_at']
        )