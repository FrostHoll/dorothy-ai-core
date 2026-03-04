import aiosqlite

from app.core.config import MemoryConfig as Config


async def create_tables(db: aiosqlite.Connection):
    await db.execute('''
                CREATE TABLE IF NOT EXISTS Memory (
                id INTEGER PRIMARY KEY,
                role TEXT,
                content TEXT,
                created_at DATETIME,
                token_count INTEGER,
                conversation_id TEXT)
            ''')
    await db.execute('''
                CREATE INDEX IF NOT EXISTS idx_id ON Memory (id)
            ''')
    await db.execute('''
                CREATE TABLE IF NOT EXISTS Conversation (
                id TEXT PRIMARY KEY,
                title TEXT,
                last_user_message TEXT,
                last_updated_at DATETIME)
            ''')
    await db.execute('''
                CREATE INDEX IF NOT EXISTS idx_conversation_id ON Conversation (id)
            ''')


async def get_db_connection() -> aiosqlite.Connection:
    db = await aiosqlite.connect(Config.db_name)
    db.row_factory = aiosqlite.Row
    await create_tables(db)
    return db
