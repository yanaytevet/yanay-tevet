from typing import Optional, List

from ninja import Schema
from pydantic import Field


class PaginationQueryParams(Schema):
    page: int = Field(0, ge=0)
    page_size: int = Field(10, ge=1, le=1000)
    order_by: Optional[List[str]] = None
    dict_filter: Optional[str] = None
