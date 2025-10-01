from pydantic import BaseModel, Field
from typing import Optional, Any, List


class MallValueSettingItem(BaseModel):
    """ProductMallValue 설정 결과 항목"""
    product_nm: str = Field(..., description="상품명")
    gubun: str = Field(..., description="구분")
    company_goods_cd: str = Field(..., description="회사 상품 코드")
    batch_id: Optional[str] = Field(None, description="배치 ID")
    xml_file_path: Optional[str] = Field(None, description="XML 파일 경로")
    excel_log_url: Optional[str] = Field(None, description="Excel 로그 URL")
    processed_count: Optional[int] = Field(None, description="처리된 개수")
    success_items: Optional[List[Any]] = Field(default=[], description="성공 항목들")
    failed_items: Optional[List[Any]] = Field(default=[], description="실패 항목들")
    error: Optional[str] = Field(None, description="오류 메시지")


class MallValueSettingResult(BaseModel):
    """ProductMallValue 설정 결과"""
    success: bool = Field(..., description="처리 성공 여부")
    message: str = Field(..., description="처리 결과 메시지")
    processed_count: int = Field(..., description="처리된 총 개수")
    success_count: int = Field(..., description="성공한 개수")
    failed_count: int = Field(..., description="실패한 개수")
    success_items: List[MallValueSettingItem] = Field(..., description="성공한 항목들")
    failed_items: List[MallValueSettingItem] = Field(..., description="실패한 항목들")


class CompleteWorkflowWithMallValueResponse(BaseModel):
    """전체 워크플로우 (상품 등록 + ProductMallValue 설정) 응답"""
    success: bool = Field(..., description="전체 처리 성공 여부")
    message: str = Field(..., description="전체 처리 결과 메시지")
    product_registration: dict[str, Any] = Field(..., description="상품 등록 워크플로우 결과")
    mall_value_setting: MallValueSettingResult = Field(..., description="ProductMallValue 설정 결과")
    overall_success: bool = Field(..., description="전체 성공 여부")
    error: Optional[str] = Field(None, description="오류 메시지")
    
    class Config:
        from_attributes = True
