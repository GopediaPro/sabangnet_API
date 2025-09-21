from pydantic import BaseModel, Field
from typing import Optional, Any


class CompleteWorkflowResponse(BaseModel):
    """전체 상품 등록 워크플로우 V2 응답"""
    success: bool = Field(..., description="처리 성공 여부")
    message: str = Field(..., description="처리 결과 메시지")
    excel_processing: dict[str, Any] = Field(..., description="Excel 처리 결과")
    database_result: dict[str, Any] = Field(..., description="데이터베이스 저장 결과")
    transfer_result: dict[str, Any] = Field(..., description="DB Transfer 결과")
    sabang_api_result: dict[str, Any] = Field(..., description="사방넷 API 요청 결과")
    error: Optional[str] = Field(None, description="오류 메시지")
    
    class Config:
        from_attributes = True
