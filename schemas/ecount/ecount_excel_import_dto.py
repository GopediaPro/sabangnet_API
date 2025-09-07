"""
Ecount Excel Import DTOs
이카운트 Excel 가져오기 API의 요청/응답 DTO
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class EcountExcelImportBaseDto(BaseModel):
    """이카운트 Excel 가져오기 기본 DTO"""
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )


class EcountExcelImportRequestDto(EcountExcelImportBaseDto):
    """이카운트 Excel 가져오기 요청 DTO"""
    
    sheet_name: str = Field("Sheet1", description="처리할 시트명")
    clear_existing: bool = Field(False, description="기존 데이터 삭제 여부")
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        json_schema_extra={
            "examples": [
                {
                    "data": {
                        "sheet_name": "Sheet1",
                        "clear_existing": False
                    },
                    "metadata": {
                        "request_id": "lyckabc"
                    }
                },
                {
                    "data": {
                        "sheet_name": "ERP_거래처코드",
                        "clear_existing": True
                    },
                    "metadata": {
                        "request_id": "lyckabc"
                    }
                }
            ]
        }
    )


class EcountExcelImportResponseDto(EcountExcelImportBaseDto):
    """이카운트 Excel 가져오기 응답 DTO"""
    
    success: bool = Field(..., description="처리 성공 여부")
    message: str = Field(..., description="처리 결과 메시지")
    imported_count: int = Field(..., description="가져온 데이터 개수")
    file_name: str = Field(..., description="처리된 파일명")
    error_details: Optional[str] = Field(None, description="오류 상세 정보")


class EcountAllDataImportRequestDto(EcountExcelImportBaseDto):
    """이카운트 모든 데이터 가져오기 요청 DTO"""
    
    clear_existing: bool = Field(False, description="기존 데이터 삭제 여부")
    erp_partner_code_sheet: str = Field("ERP_거래처코드", description="ERP 파트너 코드 시트명")
    iyes_cost_sheet: str = Field("아이예스_단가", description="IYES 단가 시트명")
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        json_schema_extra={
            "examples": [
                {
                    "data": {
                        "clear_existing": False,
                        "erp_partner_code_sheet": "ERP_거래처코드",
                        "iyes_cost_sheet": "아이예스_단가"
                    },
                    "metadata": {
                        "request_id": "lyckabc"
                    }
                },
                {
                    "data": {
                        "clear_existing": True,
                        "erp_partner_code_sheet": "거래처코드",
                        "iyes_cost_sheet": "단가정보"
                    },
                    "metadata": {
                        "request_id": "lyckabc"
                    }
                }
            ]
        }
    )


class EcountAllDataImportResultDto(EcountExcelImportBaseDto):
    """이카운트 모든 데이터 가져오기 결과 DTO"""
    
    success: bool = Field(..., description="처리 성공 여부")
    imported_count: int = Field(..., description="가져온 데이터 개수")
    file_name: str = Field(..., description="처리된 파일명")


class EcountAllDataImportResponseDto(EcountExcelImportBaseDto):
    """이카운트 모든 데이터 가져오기 응답 DTO"""
    
    success: bool = Field(..., description="전체 처리 성공 여부")
    message: str = Field(..., description="처리 결과 메시지")
    total_imported: int = Field(..., description="총 가져온 데이터 개수")
    success_count: int = Field(..., description="성공한 파일 개수")
    results: Dict[str, EcountAllDataImportResultDto] = Field(..., description="각 파일별 처리 결과")


# ERP 파트너 코드 데이터 관련 DTO
class EcountErpPartnerCodeDto(EcountExcelImportBaseDto):
    """이카운트 ERP 파트너 코드 데이터 DTO"""
    
    partner_code: Optional[str] = Field(None, description="파트너 코드")
    product_nm: Optional[str] = Field(None, description="제품명")


class EcountErpPartnerCodeImportRequestDto(EcountExcelImportRequestDto):
    """이카운트 ERP 파트너 코드 데이터 가져오기 요청 DTO"""
    pass


class EcountErpPartnerCodeImportResponseDto(EcountExcelImportResponseDto):
    """이카운트 ERP 파트너 코드 데이터 가져오기 응답 DTO"""
    pass


# IYES 단가 데이터 관련 DTO
class EcountIyesCostDto(EcountExcelImportBaseDto):
    """이카운트 IYES 단가 데이터 DTO"""
    
    product_nm: Optional[str] = Field(None, description="제품명")
    cost: Optional[int] = Field(None, description="원가(VAT 포함)")
    cost_10_vat: Optional[int] = Field(None, description="원가(VAT 10%)")
    cost_20_vat: Optional[int] = Field(None, description="원가(VAT 20%)")


class EcountIyesCostImportRequestDto(EcountExcelImportRequestDto):
    """이카운트 IYES 단가 데이터 가져오기 요청 DTO"""
    pass


class EcountIyesCostImportResponseDto(EcountExcelImportResponseDto):
    """이카운트 IYES 단가 데이터 가져오기 응답 DTO"""
    pass


# Excel 파일 검증 DTO
class EcountExcelFileValidationDto(EcountExcelImportBaseDto):
    """이카운트 Excel 파일 검증 DTO"""
    
    file_name: str = Field(..., description="파일명")
    file_size: int = Field(..., description="파일 크기 (bytes)")
    is_valid: bool = Field(..., description="파일 유효성")
    error_message: Optional[str] = Field(None, description="오류 메시지")
    supported_formats: List[str] = Field([".xlsx", ".xls"], description="지원되는 파일 형식")


# 데이터 처리 상태 DTO
class EcountDataProcessingStatusDto(EcountExcelImportBaseDto):
    """이카운트 데이터 처리 상태 DTO"""
    
    total_rows: int = Field(..., description="총 행 수")
    processed_rows: int = Field(..., description="처리된 행 수")
    skipped_rows: int = Field(..., description="건너뛴 행 수")
    error_rows: int = Field(..., description="오류 행 수")
    processing_time: float = Field(..., description="처리 시간 (초)")


# 상세 오류 정보 DTO
class EcountDataProcessingErrorDto(EcountExcelImportBaseDto):
    """이카운트 데이터 처리 오류 DTO"""
    
    row_number: int = Field(..., description="오류 발생 행 번호")
    column_name: str = Field(..., description="오류 발생 컬럼명")
    error_type: str = Field(..., description="오류 유형")
    error_message: str = Field(..., description="오류 메시지")
    raw_value: Optional[str] = Field(None, description="원본 값")


# 통계 정보 DTO
class EcountImportStatisticsDto(EcountExcelImportBaseDto):
    """이카운트 가져오기 통계 DTO"""
    
    total_files: int = Field(..., description="총 파일 수")
    successful_files: int = Field(..., description="성공한 파일 수")
    failed_files: int = Field(..., description="실패한 파일 수")
    total_imported_records: int = Field(..., description="총 가져온 레코드 수")
    total_processing_time: float = Field(..., description="총 처리 시간 (초)")
    average_processing_time_per_file: float = Field(..., description="파일당 평균 처리 시간 (초)")


# Excel 다운로드 응답 DTO
class EcountExcelDownloadResponseDto(EcountExcelImportBaseDto):
    """이카운트 Excel 다운로드 응답 DTO"""
    
    success: bool = Field(..., description="다운로드 성공 여부")
    message: str = Field(..., description="다운로드 결과 메시지")
    file_name: str = Field(..., description="다운로드된 파일명")
    file_size: int = Field(..., description="파일 크기 (bytes)")
    download_url: Optional[str] = Field(None, description="다운로드 URL")
    total_records: int = Field(..., description="총 레코드 수")
