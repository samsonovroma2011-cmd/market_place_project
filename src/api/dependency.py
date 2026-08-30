from typing import Annotated

from fastapi import Depends, Query
from pydantic import BaseModel


class PaginationParams(BaseModel):
    limit: Annotated[int, Query(1, ge=1,le=30)]
    offset: Annotated[int, Query(5, ge=0)]


PaginationDep = Annotated[PaginationParams, Depends()]