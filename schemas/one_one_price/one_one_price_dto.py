"""
1+1 상품 가격 계산을 위한 데이터 전송 객체
"""

from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field, validator


class OneOneDto(BaseModel):

    """1+1 상품 가격 계산을 위한 데이터 생성용 DTO"""

    # 상품등록 FK
    product_registration_raw_data_id: int = Field(..., description="상품등록 FK(BigInt)")

    # 상품명
    products_nm: Optional[str] = Field(None, description="상품명")

    # 기준가격(전문몰 가격)
    standard_price: Optional[Decimal] = Field(None, ge=0, description="기준가격")

    # 1+1가격, if(기준가 + 100 < 10000, roundup(기준가 * 2 + 2000, -3) - 100, roundup(기준가 * 2 + 1000, -3) - 100)
    one_one_price: Optional[Decimal] = Field(None, ge=0, description="1+1가격")

    # roundup(1+1가격 * 1.15, -3) - 100
    shop0007: Optional[Decimal] = Field(None, ge=0, description="GS Shop")
    shop0042: Optional[Decimal] = Field(None, ge=0, description="텐바이텐")
    shop0087: Optional[Decimal] = Field(None, ge=0, description="롯데홈쇼핑(신)")
    shop0094: Optional[Decimal] = Field(None, ge=0, description="무신사")
    shop0121: Optional[Decimal] = Field(None, ge=0, description="NS홈쇼핑(신)")
    shop0129: Optional[Decimal] = Field(None, ge=0, description="CJ온스타일")
    shop0154: Optional[Decimal] = Field(None, ge=0, description="K쇼핑")
    shop0650: Optional[Decimal] = Field(None, ge=0, description="홈&쇼핑(신)")

    # roundup(1+1가격 * 1.05, -3) - 100
    shop0029: Optional[Decimal] = Field(None, ge=0, description="YES24")
    shop0189: Optional[Decimal] = Field(None, ge=0, description="오늘의집")
    shop0322: Optional[Decimal] = Field(None, ge=0, description="브랜디")
    shop0444: Optional[Decimal] = Field(
        None, ge=0, description="카카오스타일 (지그재그, 포스티)")
    shop0100: Optional[Decimal] = Field(None, ge=0, description="신세계몰(신)")
    shop0298: Optional[Decimal] = Field(
        None, ge=0, description="Cafe24(신) 유튜브쇼핑")
    shop0372: Optional[Decimal] = Field(None, ge=0, description="롯데온")

    # 1+1가격 그대로 적용
    shop0381: Optional[Decimal] = Field(None, ge=0, description="에이블리")
    shop0416: Optional[Decimal] = Field(None, ge=0, description="아트박스(신)")
    shop0449: Optional[Decimal] = Field(None, ge=0, description="카카오톡선물하기")
    shop0498: Optional[Decimal] = Field(None, ge=0, description="올웨이즈")
    shop0583: Optional[Decimal] = Field(None, ge=0, description="토스쇼핑")
    shop0587: Optional[Decimal] = Field(None, ge=0, description="AliExpress")
    shop0661: Optional[Decimal] = Field(None, ge=0, description="떠리몰")
    shop0075: Optional[Decimal] = Field(None, ge=0, description="쿠팡")
    shop0319: Optional[Decimal] = Field(None, ge=0, description="도매꾹")
    shop0365: Optional[Decimal] = Field(None, ge=0, description="Grip")
    shop0387: Optional[Decimal] = Field(None, ge=0, description="하프클럽(신)")

    # 1+1가격 + 100
    shop0055: Optional[Decimal] = Field(None, ge=0, description="스마트스토어")
    shop0067: Optional[Decimal] = Field(None, ge=0, description="ESM옥션")
    shop0068: Optional[Decimal] = Field(None, ge=0, description="ESM지마켓")
    shop0273: Optional[Decimal] = Field(None, ge=0, description="카카오톡스토어")
    shop0464: Optional[Decimal] = Field(None, ge=0, description="11번가")

    @validator('standard_price', 'one_one_price', 'shop0007', 'shop0042', 'shop0087', 'shop0094', 'shop0121', 'shop0129', 'shop0154', 'shop0650', 'shop0029', 'shop0189', 'shop0322', 'shop0444', 'shop0100', 'shop0298', 'shop0372', 'shop0381', 'shop0416', 'shop0449', 'shop0498', 'shop0583', 'shop0587', 'shop0661', 'shop0075', 'shop0319', 'shop0365', 'shop0387', 'shop0055', 'shop0067', 'shop0068', 'shop0273', 'shop0464', pre=True, always=True)
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


class ProductOneOnePriceResponseDto(OneOneDto):
    """1+1 상품 가격 계산을 위한 데이터 응답용 DTO"""

    id: int = Field(..., description="고유 식별자")
    created_at: Optional[datetime] = Field(None, description="생성일시")
    updated_at: Optional[datetime] = Field(None, description="수정일시")


class ProductOneOnePriceBulkCreateDto(BaseModel):
    """1+1 상품 가격 계산을 위한 데이터 대량 생성용 DTO"""

    data: List[OneOneDto] = Field(
        ..., description="생성할 데이터 리스트")

    class Config:
        from_attributes = True


class ProductOneOnePriceBulkResponseDto(BaseModel):
    """1+1 상품 가격 계산을 위한 데이터 대량 처리 응답 DTO"""

    success_count: int = Field(..., description="성공한 데이터 수")
    error_count: int = Field(..., description="실패한 데이터 수")
    created_ids: List[int] = Field(..., description="생성된 데이터 ID 리스트")
    errors: List[str] = Field(default_factory=list, description="오류 메시지 리스트")
    success_data: List[ProductOneOnePriceResponseDto] = Field(
        default_factory=list, description="성공적으로 생성된 데이터"
    )

    class Config:
        from_attributes = True


class ExcelProcessResultDto(BaseModel):
    """Excel 처리 결과 DTO"""

    total_rows: int = Field(..., description="전체 행 수")
    valid_rows: int = Field(..., description="유효한 행 수")
    invalid_rows: int = Field(..., description="유효하지 않은 행 수")
    validation_errors: List[str] = Field(
        default_factory=list, description="검증 오류 목록")
    processed_data: List[OneOneDto] = Field(
        default_factory=list, description="처리된 데이터"
    )

    class Config:
        from_attributes = True
