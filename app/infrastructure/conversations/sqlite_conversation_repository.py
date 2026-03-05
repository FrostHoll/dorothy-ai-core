import uuid
from datetime import datetime
from typing import Optional

import aiosqlite

from app.domain.entities.conversation import Conversation
from app.domain.interfaces.conversation_repository import ConversationRepository


class SQLiteConversationsRepository(ConversationRepository):
    def __init__(self, connection: aiosqlite.Connection):
        self.connection = connection

    async def get_new_id(self) -> str:
        return str(uuid.uuid4())

    async def add(self, conversation: Conversation) -> None:
        await self.connection.execute('''
            INSERT INTO Conversation (id, platform, external_id, title, last_user_message, last_updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (conversation.id,
              conversation.platform,
              conversation.external_id,
              conversation.title,
              conversation.last_user_message,
              conversation.last_updated_at
              ))

    async def get(self, conversation_id: str) -> Optional[Conversation]:
        cursor = await self.connection.execute('''
            SELECT * FROM Conversation WHERE id = ?
        ''', (conversation_id,))
        row = await cursor.fetchone()
        await cursor.close()

        return self._row_to_conversation(row) if row else None

    async def get_id_by_metadata(self, platform: str, external_id: str) -> Optional[str]:
        cursor = await self.connection.execute('''
            SELECT id FROM Conversation
            WHERE platform = ? AND external_id = ?
        ''', (platform, external_id))
        row = await cursor.fetchone()
        await cursor.close()

        return row['id'] if row else None

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

    async def update_title(self, conversation_id: str, new_title: str) -> None:
        await self.connection.execute('''
            UPDATE Conversation
            SET title = ?
            WHERE id = ?
        ''', (new_title, conversation_id))

    @staticmethod
    def _row_to_conversation(convo_obj) -> Conversation:
        return Conversation(id=convo_obj['id'],
                            title=convo_obj['title'],
                            platform=convo_obj['platform'],
                            external_id=convo_obj['external_id'],
                            last_user_message=convo_obj['last_user_message'],
                            last_updated_at=convo_obj['last_updated_at']
                            )