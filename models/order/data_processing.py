from typing import Optional
from pydantic import BaseModel
from datetime import date

class Filters(BaseModel):
    order_date_from: Optional[date]
    order_date_to: Optional[date]
    mall_id: Optional[str]
    order_status: Optional[str] = None

class ProcessDataRequest(BaseModel):
    template_code: str
    filters: Optional[Filters] = None
    source_table: str = "receive_orders"

class ProcessDataResponse(BaseModel):
    success: bool
    template_code: str
    processed_count: int
    saved_count: int
    message: str 