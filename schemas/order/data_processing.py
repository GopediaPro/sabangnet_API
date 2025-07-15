from typing import Optional
from pydantic import BaseModel
from datetime import date

class Filters(BaseModel):
    order_date_from: Optional[date]
    order_date_to: Optional[date]
    mall_id: Optional[str] = None
    order_status: Optional[str] = None

class ProcessDataRequest(BaseModel):
    template_code: str
    created_by: Optional[str] = None
    filters: Optional[Filters] = None
    source_table: str = "receive_orders"

    class Config:
        json_schema_extra = {
            "example": {
                "template_code": "gmarket_erp",
                "created_by": "lyckabc",
                "filters": {
                    "order_date_from": "2025-07-12",
                    "order_date_to": "2025-07-14"
                },
                "source_table": "receive_orders"
            }
        }

class ProcessDataResponse(BaseModel):
    success: bool
    template_code: str
    processed_count: int
    saved_count: int
    message: str 

