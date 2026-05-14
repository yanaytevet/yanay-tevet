from typing import Generic, TypeVar, List

from ninja import Schema

T = TypeVar('T')


class PaginationOutput(Schema, Generic[T]):
    total_amount: int
    pages_amount: int
    page: int
    page_size: int
    data: List[T]
