"""
Product Registration DTO 클래스들
Excel 데이터와 API 응답을 위한 데이터 전송 객체
"""

from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field, validator


class ProductRegistrationCreateDto(BaseModel):
    """상품 등록 데이터 생성용 DTO"""
    
    products_nm: Optional[str] = Field(None, max_length=255, description="제품명")
    goods_nm: Optional[str] = Field(None, max_length=255, description="상품명")
    detail_path_img: Optional[str] = Field(None, description="상세페이지경로(이미지폴더)")
    delv_cost: Optional[Decimal] = Field(None, ge=0, description="배송비")
    goods_search: Optional[str] = Field(None, max_length=255, description="키워드")
    goods_price: Optional[Decimal] = Field(None, ge=0, description="판매가(유료배송)")
    certno: Optional[str] = Field(None, description="인증번호")
    char_process: Optional[str] = Field(None, max_length=255, description="진행옵션 가져오기")
    char_1_nm: Optional[str] = Field(None, max_length=100, description="옵션명1")
    char_1_val: Optional[str] = Field(None, description="옵션상세1")
    char_2_nm: Optional[str] = Field(None, max_length=100, description="옵션명2")
    char_2_val: Optional[str] = Field(None, description="옵션상세2")
    img_path: Optional[str] = Field(None, description="대표이미지")
    img_path1: Optional[str] = Field(None, description="부가이미지1 (종합몰이미지_jpg)")
    img_path2: Optional[str] = Field(None, description="부가이미지2")
    img_path3: Optional[str] = Field(None, description="부가이미지3")
    img_path4: Optional[str] = Field(None, description="부가이미지4")
    img_path5: Optional[str] = Field(None, description="부가이미지5")
    goods_remarks: Optional[str] = Field(None, description="상세설명")
    mobile_bn: Optional[str] = Field(None, description="모바일배너")
    one_plus_one_bn: Optional[str] = Field(None, description="1+1배너")
    goods_remarks_url: Optional[str] = Field(None, description="상세설명url")
    delv_one_plus_one: Optional[str] = Field(None, max_length=255, description="1+1옵션(배송)")

    @validator('delv_cost', 'goods_price', pre=True, always=True)
    def validate_numeric_fields(cls, v):
        """숫자 필드 검증"""
        if v in (None, '', 'nan'):
            return None
        try:
            return Decimal(str(v))
        except (ValueError, TypeError):
            return None

    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v) if v is not None else None
        }


class ProductRegistrationResponseDto(ProductRegistrationCreateDto):
    """상품 등록 데이터 응답용 DTO"""
    
    id: int = Field(..., description="고유 식별자")
    created_at: Optional[datetime] = Field(None, description="생성일시")
    updated_at: Optional[datetime] = Field(None, description="수정일시")


class ProductRegistrationBulkCreateDto(BaseModel):
    """상품 등록 데이터 대량 생성용 DTO"""
    
    data: List[ProductRegistrationCreateDto] = Field(..., description="생성할 데이터 리스트")
    
    class Config:
        from_attributes = True


class ProductRegistrationBulkResponseDto(BaseModel):
    """상품 등록 데이터 대량 처리 응답 DTO"""
    
    success_count: int = Field(..., description="성공한 데이터 수")
    error_count: int = Field(..., description="실패한 데이터 수")
    created_ids: List[int] = Field(..., description="생성된 데이터 ID 리스트")
    errors: List[str] = Field(default_factory=list, description="오류 메시지 리스트")
    success_data: List[ProductRegistrationResponseDto] = Field(
        default_factory=list, description="성공적으로 생성된 데이터"
    )
    
    class Config:
        from_attributes = True


class ExcelProcessResultDto(BaseModel):
    """Excel 처리 결과 DTO"""
    
    total_rows: int = Field(..., description="전체 행 수")
    valid_rows: int = Field(..., description="유효한 행 수")
    invalid_rows: int = Field(..., description="유효하지 않은 행 수")
    validation_errors: List[str] = Field(default_factory=list, description="검증 오류 목록")
    processed_data: List[ProductRegistrationCreateDto] = Field(
        default_factory=list, description="처리된 데이터"
    )
    
    class Config:
        from_attributes = True
