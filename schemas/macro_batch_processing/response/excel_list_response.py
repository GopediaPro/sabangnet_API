from pydantic import BaseModel
from typing import Generic, Optional, TypeVar


T = TypeVar("T")


class ExcelItem(BaseModel, Generic[T]):
    data: list[T]
    status: Optional[str] = None
    message: Optional[str] = None


class ExcelListResponse(BaseModel, Generic[T]):
    total: int
    page: int
    page_size: int
    items: list[ExcelItem[T]]
