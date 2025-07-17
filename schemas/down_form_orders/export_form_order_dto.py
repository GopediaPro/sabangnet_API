from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field
from schemas.down_form_orders.down_form_order_dto import BaseDTO, DownFormOrderDto as ExportFormOrderDto
# ExportFormOrderDto는 DownFormOrderDto의 alias로만 사용


class ExportFormOrderResponse(BaseModel):
    saved_count: int
    message: str


class ExportFormOrderFilter(BaseModel):
    template_code: Optional[str]
    date_from: Optional[datetime]
    date_to: Optional[datetime]


class ExportFormOrdersBulkDto(BaseDTO):
    success: Optional[bool] = Field(None, description="성공 여부")
    template_code: Optional[str] = Field(None, description="템플릿 코드")
    processed_count: Optional[int] = Field(None, description="처리된 데이터 수")
    saved_count: Optional[int] = Field(None, description="저장된 데이터 수")
    message: Optional[str] = Field(None, description="메시지")