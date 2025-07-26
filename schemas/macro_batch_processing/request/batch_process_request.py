from typing import Optional
from pydantic import BaseModel, Field
from schemas.receive_orders.request.receive_orders_request import BaseDateRangeRequest


class BatchProcessRequest(BaseModel):
    created_by: Optional[str] = Field(
        None, description="작성자", example="lyckabc")
    filters: Optional[BaseDateRangeRequest] = Field(
        None,
        description="날짜 필터",
        example={
            "date_from": "2025-07-12",
            "date_to": "2025-07-14"
        })

    class Config:
        json_schema_extra = {
            "example": {
                "created_by": "lyckabc",
                "filters": {
                    "date_from": "2025-07-12",
                    "date_to": "2025-07-14"
                }
            }
        }
