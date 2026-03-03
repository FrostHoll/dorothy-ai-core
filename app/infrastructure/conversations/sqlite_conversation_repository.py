from datetime import datetime
from typing import Optional

import aiosqlite

from app.domain.entities.conversation import Conversation
from app.domain.interfaces.conversation_repository import ConversationRepository


class SQLiteConversationsRepository(ConversationRepository):
    def __init__(self, connection: aiosqlite.Connection):
        self.connection = connection

    async def add(self, conversation: Conversation) -> None:
        await self.connection.execute('''
            INSERT INTO Conversation (id, title, last_user_message, last_updated_at)
            VALUES (?, ?, ?, ?)
        ''', (conversation.id, conversation.title, conversation.last_user_message, conversation.last_updated_at))

    async def get(self, conversation_id: str) -> Optional[Conversation]:
        convo_id = str(conversation_id)
        cursor = await self.connection.execute('''
            SELECT * FROM Conversation WHERE id = ?
        ''', (convo_id,))
        row = await cursor.fetchone()
        await cursor.close()

        return self._row_to_conversation(row) if row else None

    async def get_all(self) -> list[Conversation]:
        cursor = await self.connection.execute('''
            SELECT * FROM Conversation
        ''')
        rows = await cursor.fetchall()
        await cursor.close()

        return [self._row_to_conversation(row) for row in rows]

    async def update_last_info(self, conversation_id: str, last_user_message: str, last_updated_at: datetime) -> None:
        await self.connection.execute('''
            UPDATE Conversation
            SET last_user_message = ?, last_updated_at = ?
            WHERE id = ?
        ''', (last_user_message, last_updated_at, conversation_id))

    async def delete(self, conversation_id: str) -> None:
        await self.connection.execute('''
            DELETE FROM Conversation
            WHERE id = ?
        ''', (conversation_id,))

    async def delete_all(self) -> None:
        await self.connection.execute('''
            DELETE FROM Conversation
        ''')

    @staticmethod
    def _row_to_conversation(convo_obj) -> Conversation:
        return Conversation(id=convo_obj['id'],
                            title=convo_obj['title'],
                            last_user_message=convo_obj['last_user_message'],
                            last_updated_at=convo_obj['last_updated_at']
                            )