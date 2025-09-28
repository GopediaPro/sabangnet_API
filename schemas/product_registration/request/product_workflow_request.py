from pydantic import BaseModel, Field
from typing import Optional


class CompleteWorkflowRequest(BaseModel):
    """전체 상품 등록 워크플로우 V2 요청"""
    sheet_name: str = Field(default="상품등록", description="Excel 시트명")
    enable_mall_value_setting: bool = Field(default=True, description="ProductMallValue 설정 활성화 여부")
    
    class Config:
        from_attributes = True


# IntegrationRequest[CompleteWorkflowRequest] 예제 데이터
INTEGRATION_REQUEST_EXAMPLE = {
    "data": {
        "sheet_name": "상품등록"
    },
    "metadata": {
        "request_id": "lyckabc"
    }
}
