"""
1+1 상품 가격 계산을 위한 데이터 전송 객체
"""

from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field


class OneOnePriceDto(BaseModel):

    """1+1 상품 가격 계산을 위한 데이터 전송 객체"""

    # 상품등록 FK
    product_registration_raw_data_id: int = Field(..., description="상품등록 FK(BigInt)")

    # 상품명
    product_nm: Optional[str] = Field(None, description="상품명")

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

    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v) if v is not None else None
        }
