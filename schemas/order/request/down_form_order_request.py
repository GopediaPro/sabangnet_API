from typing import List
from pydantic import BaseModel, Field
from schemas.order.down_form_order_dto import DownFormOrderDto

class DownFormOrderCreate(BaseModel):
    items: List[DownFormOrderDto]

class DownFormOrderUpdate(BaseModel):
    items: List[DownFormOrderDto]

class DownFormOrderDelete(BaseModel):
    ids: List[int]

class DownFormOrderListRequest(BaseModel):
    page: int = Field(1, description="페이지 번호")
    page_size: int = Field(100, description="페이지 크기")
    # 필터/정렬 옵션 필요시 추가
