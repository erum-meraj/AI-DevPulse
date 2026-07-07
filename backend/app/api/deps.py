from typing import Annotated

from fastapi import Query

from app.db.session import get_db


class PaginationParams:
    def __init__(
        self,
        page: Annotated[int, Query(ge=1)] = 1,
        page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    ):
        self.page = page
        self.page_size = page_size


__all__ = ["PaginationParams", "get_db"]
