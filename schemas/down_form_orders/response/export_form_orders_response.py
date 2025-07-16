from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from schemas.down_form_orders.export_form_order_dto import ExportFormOrderDto, ExportFormOrdersBulkDto


class ExportFormOrderReadResponse(BaseModel):
    """다운폼 주문 읽기 응답 DTO"""

    @classmethod
    def from_dto(cls, dto: ExportFormOrderDto) -> "ExportFormOrderReadResponse":
        return cls.model_validate(dto)

    model_config = ConfigDict(
        from_attributes=True,
    )


class ExportFormOrderCreateResponse(BaseModel):
    """다운폼 주문 생성 응답 DTO"""

    @classmethod
    def from_dto(cls, dto: ExportFormOrderDto) -> "ExportFormOrderCreateResponse":
        return cls.model_validate(dto)

    model_config = ConfigDict(
        from_attributes=True,
    )


class ExportFormOrderBulkCreateResponse(BaseModel):
    success: Optional[bool] = Field(None, description="성공 여부")
    template_code: Optional[str] = Field(None, description="템플릿 코드")
    processed_count: Optional[int] = Field(None, description="처리된 데이터 수")
    saved_count: Optional[int] = Field(None, description="저장된 데이터 수")
    message: Optional[str] = Field(None, description="메시지")

    @classmethod
    def from_dto(cls, dto: ExportFormOrdersBulkDto) -> "ExportFormOrderBulkCreateResponse":
        return cls.model_validate(dto.model_dump())


class ExportFormOrderResponse(BaseModel):
    item: Optional[ExportFormOrderDto] = None
    status: Optional[str] = None  # row별 상태(success, error 등)
    message: Optional[str] = None # row별 에러 메시지 등


class ExportFormOrderBulkResponse(BaseModel):
    """CRUD 범용 응답 객체"""
    
    items: list[ExportFormOrderResponse]


class ExportFormOrderPaginationResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[ExportFormOrderResponse]
