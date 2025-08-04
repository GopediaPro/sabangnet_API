"""
Smile Excel Import DTOs
스마일배송 Excel 가져오기 API의 요청/응답 DTO
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class SmileExcelImportBaseDto(BaseModel):
    """스마일배송 Excel 가져오기 기본 DTO"""
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )


class SmileExcelImportRequestDto(SmileExcelImportBaseDto):
    """스마일배송 Excel 가져오기 요청 DTO"""
    
    sheet_name: str = Field("Sheet1", description="처리할 시트명")
    clear_existing: bool = Field(False, description="기존 데이터 삭제 여부")


class SmileExcelImportResponseDto(SmileExcelImportBaseDto):
    """스마일배송 Excel 가져오기 응답 DTO"""
    
    success: bool = Field(..., description="처리 성공 여부")
    message: str = Field(..., description="처리 결과 메시지")
    imported_count: int = Field(..., description="가져온 데이터 개수")
    file_name: str = Field(..., description="처리된 파일명")
    error_details: Optional[str] = Field(None, description="오류 상세 정보")


class SmileAllDataImportRequestDto(SmileExcelImportBaseDto):
    """스마일배송 모든 데이터 가져오기 요청 DTO"""
    
    clear_existing: bool = Field(False, description="기존 데이터 삭제 여부")


class SmileAllDataImportResultDto(SmileExcelImportBaseDto):
    """스마일배송 모든 데이터 가져오기 결과 DTO"""
    
    success: bool = Field(..., description="처리 성공 여부")
    imported_count: int = Field(..., description="가져온 데이터 개수")
    file_name: str = Field(..., description="처리된 파일명")


class SmileAllDataImportResponseDto(SmileExcelImportBaseDto):
    """스마일배송 모든 데이터 가져오기 응답 DTO"""
    
    success: bool = Field(..., description="전체 처리 성공 여부")
    message: str = Field(..., description="처리 결과 메시지")
    total_imported: int = Field(..., description="총 가져온 데이터 개수")
    success_count: int = Field(..., description="성공한 파일 개수")
    results: Dict[str, SmileAllDataImportResultDto] = Field(..., description="각 파일별 처리 결과")


# ERP 데이터 관련 DTO
class SmileErpDataDto(SmileExcelImportBaseDto):
    """스마일배송 ERP 데이터 DTO"""
    
    date: datetime = Field(..., description="날짜")
    site: str = Field(..., description="사이트")
    customer_name: str = Field(..., description="고객성함")
    order_number: str = Field(..., description="주문번호")
    erp_code: Optional[str] = Field(None, description="ERP 코드")


class SmileErpDataImportRequestDto(SmileExcelImportRequestDto):
    """스마일배송 ERP 데이터 가져오기 요청 DTO"""
    pass


class SmileErpDataImportResponseDto(SmileExcelImportResponseDto):
    """스마일배송 ERP 데이터 가져오기 응답 DTO"""
    pass


# 정산 데이터 관련 DTO
class SmileSettlementDataDto(SmileExcelImportBaseDto):
    """스마일배송 정산 데이터 DTO"""
    
    order_number: str = Field(..., description="주문번호")
    product_number: str = Field(..., description="상품번호")
    cart_number: str = Field(..., description="장바구니번호")
    product_name: str = Field(..., description="상품명")
    buyer_name: str = Field(..., description="구매자명")
    payment_confirmation_date: Optional[datetime] = Field(None, description="입금확인일")
    delivery_completion_date: Optional[datetime] = Field(None, description="배송완료일")
    early_settlement_date: Optional[datetime] = Field(None, description="조기정산일자")
    settlement_type: Optional[str] = Field(None, description="구분")
    sales_amount: Optional[float] = Field(None, description="판매금액")
    service_fee: Optional[float] = Field(None, description="서비스이용료")
    settlement_amount: Optional[float] = Field(None, description="정산금액")
    transfer_amount: Optional[float] = Field(None, description="송금대상액")
    payment_date: Optional[datetime] = Field(None, description="결제일")
    shipping_date: Optional[datetime] = Field(None, description="발송일")
    refund_date: Optional[datetime] = Field(None, description="환불일")
    site: str = Field(..., description="사이트")


class SmileSettlementDataImportRequestDto(SmileExcelImportRequestDto):
    """스마일배송 정산 데이터 가져오기 요청 DTO"""
    pass


class SmileSettlementDataImportResponseDto(SmileExcelImportResponseDto):
    """스마일배송 정산 데이터 가져오기 응답 DTO"""
    pass


# SKU 데이터 관련 DTO
class SmileSkuDataDto(SmileExcelImportBaseDto):
    """스마일배송 SKU 데이터 DTO"""
    
    sku_number: str = Field(..., description="SKU번호")
    model_name: str = Field(..., description="모델명")
    sku_name: Optional[str] = Field(None, description="SKU명")
    comment: Optional[str] = Field(None, description="코멘트")


class SmileSkuDataImportRequestDto(SmileExcelImportRequestDto):
    """스마일배송 SKU 데이터 가져오기 요청 DTO"""
    pass


class SmileSkuDataImportResponseDto(SmileExcelImportResponseDto):
    """스마일배송 SKU 데이터 가져오기 응답 DTO"""
    pass


# Excel 파일 검증 DTO
class SmileExcelFileValidationDto(SmileExcelImportBaseDto):
    """스마일배송 Excel 파일 검증 DTO"""
    
    file_name: str = Field(..., description="파일명")
    file_size: int = Field(..., description="파일 크기 (bytes)")
    is_valid: bool = Field(..., description="파일 유효성")
    error_message: Optional[str] = Field(None, description="오류 메시지")
    supported_formats: List[str] = Field([".xlsx", ".xls"], description="지원되는 파일 형식")


# 데이터 처리 상태 DTO
class SmileDataProcessingStatusDto(SmileExcelImportBaseDto):
    """스마일배송 데이터 처리 상태 DTO"""
    
    total_rows: int = Field(..., description="총 행 수")
    processed_rows: int = Field(..., description="처리된 행 수")
    skipped_rows: int = Field(..., description="건너뛴 행 수")
    error_rows: int = Field(..., description="오류 행 수")
    processing_time: float = Field(..., description="처리 시간 (초)")


# 상세 오류 정보 DTO
class SmileDataProcessingErrorDto(SmileExcelImportBaseDto):
    """스마일배송 데이터 처리 오류 DTO"""
    
    row_number: int = Field(..., description="오류 발생 행 번호")
    column_name: str = Field(..., description="오류 발생 컬럼명")
    error_type: str = Field(..., description="오류 유형")
    error_message: str = Field(..., description="오류 메시지")
    raw_value: Optional[str] = Field(None, description="원본 값")


# 통계 정보 DTO
class SmileImportStatisticsDto(SmileExcelImportBaseDto):
    """스마일배송 가져오기 통계 DTO"""
    
    total_files: int = Field(..., description="총 파일 수")
    successful_files: int = Field(..., description="성공한 파일 수")
    failed_files: int = Field(..., description="실패한 파일 수")
    total_imported_records: int = Field(..., description="총 가져온 레코드 수")
    total_processing_time: float = Field(..., description="총 처리 시간 (초)")
    average_processing_time_per_file: float = Field(..., description="파일당 평균 처리 시간 (초)") 