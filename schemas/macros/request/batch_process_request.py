from typing import Optional
from pydantic import BaseModel, Field
from schemas.receive_orders.request.receive_orders_request import BaseDateRangeRequest


class BatchProcessRequest(BaseModel):
    template_code: str = Field(..., description="템플릿 코드")
    created_by: Optional[str] = None
    filters: Optional[BaseDateRangeRequest] = None
    source_table: str = "receive_orders"

    class Config:
        json_schema_extra = {
            "example": {
                "template_code": "gmarket_erp",
                "created_by": "lyckabc",
                "filters": {
                    "date_from": "2025-07-12",
                    "date_to": "2025-07-14"
                },
                "source_table": "receive_orders"
            }
        }
