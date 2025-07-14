from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from schemas.order.down_form_order_dto import DownFormOrderDto as ExportFormOrderDto

# ExportFormOrderDto는 DownFormOrderDto의 alias로만 사용

class ExportFormOrderRequest(BaseModel):
    template_code: str = Field(..., description="템플릿 코드")
    raw_data: List[Dict[str, Any]] = Field(..., description="원본 주문 데이터")

class ExportFormOrderResponse(BaseModel):
    saved_count: int
    message: str

class ExportFormOrderFilter(BaseModel):
    template_code: Optional[str]
    date_from: Optional[datetime]
    date_to: Optional[datetime]