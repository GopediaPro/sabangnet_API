from typing import Optional
from pydantic import BaseModel, Field


class ExcelRunMacroRequest(BaseModel):
    """
    엑셀 매크로 실행 요청 객체
    """
    template_code: str = Field(..., description="템플릿 코드")
    created_by: Optional[str] = Field(None, description="생성자")
    source_table: str = Field(default="receive_orders", description="소스 테이블")

    class Config:
        json_schema_extra = {
            "example": {
                "template_code": "gmarket_erp",
                "created_by": "lyckabc",
                "source_table": "receive_orders"
            }
        } 