"""
Product Registration DTOs
상품 등록 관련 데이터 전송 객체
"""

import logging
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

logger = logging.getLogger(__name__)

logger.info("Product Registration DTO 모듈 로드 시작...")


class ProductRegistrationCreateDto(BaseModel):
    """상품 등록 생성 DTO - Excel 데이터 구조에 맞춤"""
    # 기본 정보
    product_nm: str = Field(..., description="제품명")
    goods_nm: Optional[str] = Field(None, description="상품명")
    detail_path_img: Optional[str] = Field(None, description="상세페이지경로(이미지폴더)")
    
    # 배송 및 가격 정보
    delv_cost: Optional[float] = Field(None, description="배송비")
    goods_search: Optional[str] = Field(None, description="키워드")
    goods_price: Optional[float] = Field(None, description="판매가(유료배송)")
    
    # 인증 및 진행 옵션
    certno: Optional[str] = Field(None, description="인증번호")
    char_process: Optional[str] = Field(None, description="진행옵션 가져오기")
    
    # 옵션 정보
    char_1_nm: Optional[str] = Field(None, description="옵션명1")
    char_1_val: Optional[str] = Field(None, description="옵션상세1")
    char_2_nm: Optional[str] = Field(None, description="옵션명2")
    char_2_val: Optional[str] = Field(None, description="옵션상세2")
    
    # 이미지 정보
    img_path: Optional[str] = Field(None, description="대표이미지")
    img_path1: Optional[str] = Field(None, description="종합몰(JPG)이미지")
    img_path2: Optional[str] = Field(None, description="부가이미지2")
    img_path3: Optional[str] = Field(None, description="부가이미지3")
    img_path4: Optional[str] = Field(None, description="부가이미지4")
    img_path5: Optional[str] = Field(None, description="부가이미지5")
    
    # 상세 정보
    goods_remarks: Optional[str] = Field(None, description="상세설명")
    mobile_bn: Optional[str] = Field(None, description="모바일배너")
    one_plus_one_bn: Optional[str] = Field(None, description="1+1배너")
    goods_remarks_url: Optional[str] = Field(None, description="상세설명url")
    delv_one_plus_one: Optional[str] = Field(None, description="1+1옵션(배송)")
    delv_one_plus_one_detail: Optional[str] = Field(None, description="1+1옵션상세")
    stock_use_yn: Optional[str] = Field(None, description="재고관리사용여부")
    
    # 카테고리 정보
    class_nm1: Optional[str] = Field(None, description="대분류_분류명")
    class_nm2: Optional[str] = Field(None, description="중분류_분류명")
    class_nm3: Optional[str] = Field(None, description="소분류_분류명")
    class_nm4: Optional[str] = Field(None, description="세분류_분류명")
    
    class Config:
        from_attributes = True


logger.info("ProductRegistrationCreateDto 정의 완료")


class ProductRegistrationResponseDto(BaseModel):
    """상품 등록 응답 DTO - Excel 데이터 구조에 맞춤"""
    id: int = Field(..., description="상품 ID")
    
    # 기본 정보
    product_nm: str = Field(..., description="제품명")
    goods_nm: Optional[str] = Field(None, description="상품명")
    detail_path_img: Optional[str] = Field(None, description="상세페이지경로(이미지폴더)")
    
    # 배송 및 가격 정보
    delv_cost: Optional[float] = Field(None, description="배송비")
    goods_search: Optional[str] = Field(None, description="키워드")
    goods_price: Optional[float] = Field(None, description="판매가(유료배송)")
    
    # 인증 및 진행 옵션
    certno: Optional[str] = Field(None, description="인증번호")
    char_process: Optional[str] = Field(None, description="진행옵션 가져오기")
    
    # 옵션 정보
    char_1_nm: Optional[str] = Field(None, description="옵션명1")
    char_1_val: Optional[str] = Field(None, description="옵션상세1")
    char_2_nm: Optional[str] = Field(None, description="옵션명2")
    char_2_val: Optional[str] = Field(None, description="옵션상세2")
    
    # 이미지 정보
    img_path: Optional[str] = Field(None, description="대표이미지")
    img_path1: Optional[str] = Field(None, description="종합몰(JPG)이미지")
    img_path2: Optional[str] = Field(None, description="부가이미지2")
    img_path3: Optional[str] = Field(None, description="부가이미지3")
    img_path4: Optional[str] = Field(None, description="부가이미지4")
    img_path5: Optional[str] = Field(None, description="부가이미지5")
    
    # 상세 정보
    goods_remarks: Optional[str] = Field(None, description="상세설명")
    mobile_bn: Optional[str] = Field(None, description="모바일배너")
    one_plus_one_bn: Optional[str] = Field(None, description="1+1배너")
    goods_remarks_url: Optional[str] = Field(None, description="상세설명url")
    delv_one_plus_one: Optional[str] = Field(None, description="1+1옵션(배송)")
    delv_one_plus_one_detail: Optional[str] = Field(None, description="1+1옵션상세")
    
    # 카테고리 정보
    class_nm1: Optional[str] = Field(None, description="대분류_분류명")
    class_nm2: Optional[str] = Field(None, description="중분류_분류명")
    class_nm3: Optional[str] = Field(None, description="소분류_분류명")
    class_nm4: Optional[str] = Field(None, description="세분류_분류명")
    
    # 타임스탬프
    created_at: datetime = Field(..., description="생성일시")
    updated_at: datetime = Field(..., description="수정일시")
    
    class Config:
        from_attributes = True


logger.info("ProductRegistrationResponseDto 정의 완료")


class ProductRegistrationBulkCreateDto(BaseModel):
    """대량 상품 등록 생성 DTO"""
    data: List[ProductRegistrationCreateDto] = Field(..., description="상품 등록 데이터 목록")


logger.info("ProductRegistrationBulkCreateDto 정의 완료")


class ProductRegistrationBulkResponseDto(BaseModel):
    """대량 상품 등록 응답 DTO"""
    success_count: int = Field(..., description="성공한 데이터 수")
    error_count: int = Field(..., description="실패한 데이터 수")
    created_ids: List[int] = Field(..., description="생성된 데이터 ID 목록")
    errors: List[str] = Field(..., description="오류 메시지 목록")
    success_data: List[ProductRegistrationResponseDto] = Field(..., description="성공한 데이터 목록")


logger.info("ProductRegistrationBulkResponseDto 정의 완료")


class ExcelProcessResultDto(BaseModel):
    """Excel 처리 결과 DTO"""
    total_rows: int = Field(..., description="총 행 수")
    valid_rows: int = Field(..., description="유효한 행 수")
    invalid_rows: int = Field(..., description="무효한 행 수")
    validation_errors: List[str] = Field(..., description="검증 오류 목록")
    processed_data: List[ProductRegistrationCreateDto] = Field(..., description="처리된 데이터 목록")


logger.info("ExcelProcessResultDto 정의 완료")


class ExcelImportResponseDto(BaseModel):
    """Excel 가져오기 응답 DTO"""
    message: str = Field(..., description="처리 결과 메시지")
    excel_processing: ExcelProcessResultDto = Field(..., description="Excel 처리 결과")
    database_result: ProductRegistrationBulkResponseDto = Field(..., description="데이터베이스 저장 결과")


logger.info("ExcelImportResponseDto 정의 완료")


class CompleteWorkflowResponseDto(BaseModel):
    """전체 워크플로우 응답 DTO"""
    success: bool = Field(..., description="처리 성공 여부")
    message: str = Field(..., description="처리 결과 메시지")
    excel_processing: Dict[str, Any] = Field(..., description="Excel 처리 결과")
    database_result: Dict[str, Any] = Field(..., description="데이터베이스 저장 결과")
    transfer_result: Dict[str, Any] = Field(..., description="DB Transfer 결과")
    sabang_api_result: Dict[str, Any] = Field(..., description="사방넷 API 요청 결과")
    error: Optional[str] = Field(None, description="오류 메시지")


logger.info("CompleteWorkflowResponseDto 정의 완료")
logger.info("Product Registration DTO 모듈 로드 완료")
