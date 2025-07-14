from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from schemas.order.down_form_order_dto import DownFormOrdersBulkDto, DownFormOrderDto


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


class DownFormOrderBulkCreateResponse(BaseModel):
    success: Optional[bool] = Field(None, description="성공 여부")
    template_code: Optional[str] = Field(None, description="템플릿 코드")
    processed_count: Optional[int] = Field(None, description="처리된 데이터 수")
    saved_count: Optional[int] = Field(None, description="저장된 데이터 수")
    message: Optional[str] = Field(None, description="메시지")

    @classmethod
    def from_dto(cls, dto: DownFormOrdersBulkDto) -> "DownFormOrderBulkCreateResponse":
        return cls.model_validate(dto.model_dump())


class DownFormOrderResponse(BaseModel):
    item: Optional[DownFormOrderDto] = None
    status: Optional[str] = None  # row별 상태(success, error 등)
    message: Optional[str] = None # row별 에러 메시지 등


class DownFormOrderBulkResponse(BaseModel):
    items: list[DownFormOrderResponse]


class DownFormOrderPaginationResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[DownFormOrderResponse]
