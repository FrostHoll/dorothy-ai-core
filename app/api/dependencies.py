import aiosqlite
from typing import Annotated, AsyncIterator

from fastapi.params import Depends
from starlette.requests import Request

from app.application.container import Container
from app.application.unit_of_work import AbstractUnitOfWork
from app.infrastructure.sqlite_db import get_db_connection
from app.infrastructure.sqlite_unit_of_work import SQLiteUnitOfWork

def get_container(request: Request) -> Container:
    return request.app.state.container

ContainerDep = Annotated[Container, Depends(get_container)]

async def get_db() -> AsyncIterator[aiosqlite.Connection]:
    db = await get_db_connection()
    try:
        yield db
    finally:
        await db.close()


async def get_uow(
        db: aiosqlite.Connection = Depends(get_db)
) -> AbstractUnitOfWork:
    return SQLiteUnitOfWork(db)


UOWDep = Annotated[AbstractUnitOfWork, Depends(get_uow)]