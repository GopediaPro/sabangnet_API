from datetime import date
from pydantic import BaseModel, Field

class SmileMacroV2Request(BaseModel):
    order_date_from: date = Field(..., description="주문 시작 일자", example="2025-01-01")
    order_date_to: date = Field(..., description="주문 종료 일자", example="2025-01-31")
    
    class Config:
        json_schema_extra = {
            "example": {
                "order_date_from": "2025-01-01",
                "order_date_to": "2025-01-31"
            }
        }
