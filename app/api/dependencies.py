import aiosqlite
from typing import Annotated

from fastapi.params import Depends

from app.application.memory_manager import MemoryManager
from app.core.config import MemoryConfig
from app.domain.interfaces.memory_repository import MemoryRepository
from app.infrastructure.memory.sqlite_memory import SQLiteMemory


async def get_connection():
    async with aiosqlite.connect(MemoryConfig.db_name) as conn:
        conn.row_factory = aiosqlite.Row
        yield conn

ConnectionDep = Annotated[aiosqlite.Connection, Depends(get_connection)]

def get_memory_repository(
        connection: ConnectionDep
):
    return SQLiteMemory(connection)

MemoryRepositoryDep = Annotated[MemoryRepository, Depends(get_memory_repository)]

def get_memory_manager(
        repository: MemoryRepositoryDep
):
    return MemoryManager(repository)

MemoryManagerDep = Annotated[MemoryManager, Depends(get_memory_manager)]