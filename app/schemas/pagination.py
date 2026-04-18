from pydantic import BaseModel
from typing import Generic, TypeVar

T = TypeVar("T")


class PaginationResponse(BaseModel, Generic[T]):
    total: int
    page: int
    page_size: int
    total_pages: int
    items: list[T]
