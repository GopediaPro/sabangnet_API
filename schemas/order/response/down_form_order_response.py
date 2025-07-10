from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, ConfigDict, Field
from schemas.order.down_form_order_dto import DownFormOrderDto


class DownFormOrderReadResponse(BaseModel):
    """다운폼 주문 읽기 응답 DTO"""

    @classmethod
    def from_dto(cls, dto: DownFormOrderDto) -> "DownFormOrderReadResponse":
        return cls.model_validate(dto)

    model_config = ConfigDict(
        from_attributes=True,
    )


class DownFormOrderCreateResponse(BaseModel):
    """다운폼 주문 생성 응답 DTO"""

    @classmethod
    def from_dto(cls, dto: DownFormOrderDto) -> "DownFormOrderCreateResponse":
        return cls.model_validate(dto)

    model_config = ConfigDict(
        from_attributes=True,
    )


class DownFormOrderItem(BaseModel):
    data: List[DownFormOrderDto]
    status: Optional[str] = None  # row별 상태(success, error 등)
    message: Optional[str] = None # row별 에러 메시지 등

class DownFormOrderListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[DownFormOrderItem]

class DownFormOrderBulkResponse(BaseModel):
    results: List[DownFormOrderItem]