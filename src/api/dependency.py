from typing import Annotated

from fastapi import Depends, Query
from pydantic import BaseModel

from src.database import async_session_maker
from src.utils.db_manager import DBManager


class PaginationParams(BaseModel):
    limit: Annotated[int, Query(1, ge=1,le=30)]
    offset: Annotated[int, Query(5, ge=0)]


PaginationDep = Annotated[PaginationParams, Depends()]


def get_db():
    async with DBManager(session_factory=async_session_maker) as db:
        yield db

DBDep = Annotated[DBManager, Depends(get_db)]