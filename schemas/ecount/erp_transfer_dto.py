"""
ERP Transfer DTOs
ERP 데이터 전송을 위한 요청/응답 스키마
"""

from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


class FormNameType(str, Enum):
    """Form Name 타입 정의"""
    OKMART_ERP_SALE_OK = "okmart_erp_sale_ok"
    OKMART_ERP_SALE_IYES = "okmart_erp_sale_iyes"
    IYES_ERP_SALE_IYES = "iyes_erp_sale_iyes"
    IYES_ERP_PURCHASE_IYES = "iyes_erp_purchase_iyes"


class ErpTransferRequestDto(BaseModel):
    """ERP 전송 요청 DTO"""
    
    date_from: datetime = Field(..., description="조회 시작일시")
    date_to: datetime = Field(..., description="조회 종료일시")
    form_name: FormNameType = Field(..., description="Form Name 타입")
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "date_from": "2025-01-01T00:00:00",
                    "date_to": "2025-09-30T23:59:59",
                    "form_name": "okmart_erp_sale_ok"
                },
                {
                    "date_from": "2025-01-01T00:00:00",
                    "date_to": "2025-09-30T23:59:59",
                    "form_name": "okmart_erp_sale_iyes"
                },
                {
                    "date_from": "2025-01-01T00:00:00",
                    "date_to": "2025-09-30T23:59:59",
                    "form_name": "iyes_erp_sale_iyes"
                },
                {
                    "date_from": "2025-01-01T00:00:00",
                    "date_to": "2025-09-30T23:59:59",
                    "form_name": "iyes_erp_purchase_iyes"
                }
            ]
        }
    
    @validator('date_to')
    def validate_date_range(cls, v, values):
        """날짜 범위 검증"""
        if 'date_from' in values and v <= values['date_from']:
            raise ValueError('date_to must be after date_from')
        return v


class ErpTransferResponseDto(BaseModel):
    """ERP 전송 응답 DTO"""
    
    batch_id: str = Field(..., description="배치 ID")
    total_records: int = Field(..., description="총 레코드 수")
    processed_records: int = Field(..., description="처리된 레코드 수")
    excel_file_name: str = Field(..., description="생성된 Excel 파일명")
    download_url: Optional[str] = Field(None, description="다운로드 URL")
    file_size: Optional[int] = Field(None, description="파일 크기 (bytes)")
    form_name: str = Field(..., description="처리된 Form Name")
    date_range: Dict[str, str] = Field(..., description="조회 날짜 범위")
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "batch_id": "batch_20250101_001",
                    "total_records": 150,
                    "processed_records": 150,
                    "excel_file_name": "ERP업로드용_okmart_erp_sale_ok_20250101_001.xlsx",
                    "download_url": "https://minio.example.com/excel/okmart_erp_sale_ok/20250101120000_ERP업로드용_okmart_erp_sale_ok_20250101_001.xlsx",
                    "file_size": 1024000,
                    "form_name": "okmart_erp_sale_ok",
                    "date_range": {
                        "from": "2025-01-01T00:00:00",
                        "to": "2025-09-30T23:59:59"
                    }
                }
            ]
        }


class ErpTransferDataDto(BaseModel):
    """ERP 전송 데이터 DTO (Excel 생성용)"""
    
    # 기본 정보
    idx: str = Field(..., description="사방넷주문번호")
    order_id: Optional[str] = Field(None, description="주문ID")
    mall_order_id: Optional[str] = Field(None, description="쇼핑몰주문ID")
    
    # 상품 정보
    product_id: Optional[str] = Field(None, description="상품ID")
    product_name: Optional[str] = Field(None, description="상품명")
    mall_product_id: Optional[str] = Field(None, description="쇼핑몰상품ID")
    item_name: Optional[str] = Field(None, description="아이템명")
    sku_value: Optional[str] = Field(None, description="SKU 값")
    sku_alias: Optional[str] = Field(None, description="SKU 별칭")
    sku_no: Optional[str] = Field(None, description="SKU 번호")
    barcode: Optional[str] = Field(None, description="바코드")
    model_name: Optional[str] = Field(None, description="모델명")
    erp_model_name: Optional[str] = Field(None, description="ERP 모델명")
    
    # 수량 및 판매 정보
    sale_cnt: Optional[str] = Field(None, description="판매수량")
    
    # 금액 정보
    pay_cost: Optional[float] = Field(None, description="결제금액")
    delv_cost: Optional[float] = Field(None, description="배송비")
    total_cost: Optional[float] = Field(None, description="총금액")
    expected_payout: Optional[float] = Field(None, description="예상정산금액")
    service_fee: Optional[float] = Field(None, description="서비스이용료")
    
    # 수취인 정보
    receive_name: Optional[str] = Field(None, description="수취인명")
    receive_cel: Optional[str] = Field(None, description="수취인휴대폰")
    receive_tel: Optional[str] = Field(None, description="수취인전화")
    receive_addr: Optional[str] = Field(None, description="수취인주소")
    receive_zipcode: Optional[str] = Field(None, description="수취인우편번호")
    
    # 배송 정보
    delv_msg: Optional[str] = Field(None, description="배송메시지")
    delivery_id: Optional[str] = Field(None, description="배송ID")
    delivery_class: Optional[str] = Field(None, description="배송구분")
    invoice_no: Optional[str] = Field(None, description="송장번호")
    
    # 기타 정보
    fld_dsp: Optional[str] = Field(None, description="필드 설명")
    order_date: Optional[datetime] = Field(None, description="주문일자")
    reg_date: Optional[str] = Field(None, description="등록일자")
    
    class Config:
        from_attributes = True
