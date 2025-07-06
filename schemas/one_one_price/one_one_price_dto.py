"""
1+1 상품 가격 계산을 위한 데이터 전송 객체
"""

from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field


class OneOnePriceDto(BaseModel):

    """1+1 상품 가격 계산을 위한 데이터 전송 객체"""

    # 품번코드대량등록툴 FK
    test_product_raw_data_id: int = Field(..., alias="test_product_raw_data_id", description="품번코드대량등록툴 FK")

    # 상품명
    product_nm: str = Field(..., description="상품명")

    # 자체상품코드
    compayny_goods_cd: str = Field(..., description="자체상품코드")

    # 기준가격(전문몰 가격)
    standard_price: Optional[Decimal] = Field(..., description="기준가격")

    # 1+1가격, if(기준가 + 100 < 10000, roundup(기준가 * 2 + 2000, -3) - 100, roundup(기준가 * 2 + 1000, -3) - 100)
    one_one_price: Optional[Decimal] = Field(..., description="1+1가격")

    # roundup(1+1가격 * 1.15, -3) - 100
    shop0007: Optional[Decimal] = Field(..., description="GS Shop")
    shop0042: Optional[Decimal] = Field(..., description="텐바이텐")
    shop0087: Optional[Decimal] = Field(..., description="롯데홈쇼핑(신)")
    shop0094: Optional[Decimal] = Field(..., description="무신사")
    shop0121: Optional[Decimal] = Field(..., description="NS홈쇼핑(신)")
    shop0129: Optional[Decimal] = Field(..., description="CJ온스타일")
    shop0154: Optional[Decimal] = Field(..., description="K쇼핑")
    shop0650: Optional[Decimal] = Field(..., description="홈&쇼핑(신)")

    # roundup(1+1가격 * 1.05, -3) - 100
    shop0029: Optional[Decimal] = Field(..., description="YES24")
    shop0189: Optional[Decimal] = Field(..., description="오늘의집")
    shop0322: Optional[Decimal] = Field(..., description="브랜디")
    shop0444: Optional[Decimal] = Field(..., description="카카오스타일 (지그재그, 포스티)")
    shop0100: Optional[Decimal] = Field(..., description="신세계몰(신)")
    shop0298: Optional[Decimal] = Field(..., description="Cafe24(신) 유튜브쇼핑")
    shop0372: Optional[Decimal] = Field(..., description="롯데온")

    # 1+1가격 그대로 적용
    shop0381: Optional[Decimal] = Field(..., description="에이블리")
    shop0416: Optional[Decimal] = Field(..., description="아트박스(신)")
    shop0449: Optional[Decimal] = Field(..., description="카카오톡선물하기")
    shop0498: Optional[Decimal] = Field(..., description="올웨이즈")
    shop0583: Optional[Decimal] = Field(..., description="토스쇼핑")
    shop0587: Optional[Decimal] = Field(..., description="AliExpress")
    shop0661: Optional[Decimal] = Field(..., description="떠리몰")
    shop0075: Optional[Decimal] = Field(..., description="쿠팡")
    shop0319: Optional[Decimal] = Field(..., description="도매꾹")
    shop0365: Optional[Decimal] = Field(..., description="Grip")
    shop0387: Optional[Decimal] = Field(..., description="하프클럽(신)")

    # 1+1가격 + 100
    shop0055: Optional[Decimal] = Field(..., description="스마트스토어")
    shop0067: Optional[Decimal] = Field(..., description="ESM옥션")
    shop0068: Optional[Decimal] = Field(..., description="ESM지마켓")
    shop0273: Optional[Decimal] = Field(..., description="카카오톡스토어")
    shop0464: Optional[Decimal] = Field(..., description="11번가")

    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v) if v is not None else None
        }


class OneOnePriceBulkDto(BaseModel):
    success_count: int = Field(..., description="성공 건수")
    error_count: int = Field(..., description="실패 건수")
    created_product_nm: List[int] = Field(..., description="성공 상품명")
    errors: List[str] = Field(..., description="실패 에러")
    success_data: List[OneOnePriceDto] = Field(..., description="성공 데이터")

    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v) if v is not None else None
        }