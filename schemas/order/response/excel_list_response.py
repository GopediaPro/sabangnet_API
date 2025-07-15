from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel

T = TypeVar("T")

class ExcelItem(BaseModel, Generic[T]):
    data: List[T]
    status: Optional[str] = None
    message: Optional[str] = None

class ExcelListResponse(BaseModel, Generic[T]):
    total: int
    page: int
    page_size: int
    items: List[ExcelItem[T]]
