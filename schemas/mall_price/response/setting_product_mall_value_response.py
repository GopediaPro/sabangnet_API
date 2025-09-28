from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class SettingProductMallValueResponse(BaseModel):
    success: bool = Field(..., description="성공 여부")
    message: str = Field(..., description="응답 메시지")
    batch_id: int = Field(..., description="배치 ID")
    xml_file_path: str = Field(..., description="XML 파일 경로")
    excel_log_url: str = Field(..., description="Excel 로그 파일 URL")
    processed_count: int = Field(..., description="처리된 총 개수")
    success_items: List[Dict[str, Any]] = Field(..., description="성공한 항목들")
    failed_items: List[Dict[str, Any]] = Field(..., description="실패한 항목들")
    product_mall_value: Dict[str, Any] = Field(..., description="ProductMallValue 데이터")

    class Config:
        from_attributes = True
