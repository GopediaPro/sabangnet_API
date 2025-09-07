from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Optional, TypeVar, Generic


# 제네릭 타입 변수 정의
T = TypeVar('T')


class Metadata(BaseModel):
    request_id: Optional[str] = Field(None, description="요청 ID")


class IntegrationRequest(BaseModel, Generic[T]):
    data: T = Field(..., description="데이터")
    metadata: Metadata = Field(..., description="메타데이터")
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "data": {
                        "date_from": "2025-01-01T00:00:00",
                        "date_to": "2025-09-30T23:59:59",
                        "form_name": "okmart_erp_sale_ok"
                    },
                    "metadata": {
                        "request_id": "lyckabc"
                    }
                },
                {
                    "data": {
                        "date_from": "2025-01-01T00:00:00",
                        "date_to": "2025-09-30T23:59:59",
                        "form_name": "okmart_erp_sale_iyes"
                    },
                    "metadata": {
                        "request_id": "lyckabc"
                    }
                }
            ]
        }