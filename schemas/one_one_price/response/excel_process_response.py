from typing import List
from pydantic import BaseModel, Field
from schemas.one_one_price.one_one_price_dto import OneOnePriceDto


class ExcelProcessResponse(BaseModel):
    """Excel 처리 결과 DTO"""

    total_rows: int = Field(..., description="전체 행 수")
    valid_rows: int = Field(..., description="유효한 행 수")
    invalid_rows: int = Field(..., description="유효하지 않은 행 수")
    validation_errors: List[str] = Field(
        default_factory=list, description="검증 오류 목록")
    processed_data: List[OneOnePriceDto] = Field(
        default_factory=list, description="처리된 데이터"
    )

    class Config:
        from_attributes = True