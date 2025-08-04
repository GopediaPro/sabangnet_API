from pydantic import BaseModel, Field
from typing import Any


class BulkRunMacroResponse(BaseModel):
    total_saved_count: int = Field(..., description="저장된 총 개수")
    successful_results: list[dict[str, Any]] = Field(..., description="성공한 결과")
    failed_results: list[dict[str, Any]] = Field(..., description="실패한 결과")

    @classmethod
    def build_total(cls, total_saved_count: int, successful_results: list[dict[str, Any]], failed_results: list[dict[str, Any]]):
        return cls(
            total_saved_count=total_saved_count,
            successful_results=successful_results,
            failed_results=failed_results
        )
    