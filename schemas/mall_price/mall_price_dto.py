from pydantic import BaseModel, Field


class MallPriceDto(BaseModel):

    class Config:
        from_attributes = True

    products_nm: str = Field(..., description="상품코드")
    product_registration_raw_data_id: int = Field(..., description="product_registration_raw_data ID (fk)")
    standard_price: int = Field(..., description="기준 가격")

    # ((기본판매가 + (기본판매가 * 0.15)) 1000자리에서 반올림 후 - 100) + 3000
    shop0007: int = Field(..., description="gs shop 가격")
    shop0042: int = Field(..., description="텐바이텐 가격")
    shop0087: int = Field(..., description="롯데홈쇼핑 가격")
    shop0094: int = Field(..., description="무신사 가격")
    shop0121: int = Field(..., description="ns홈쇼핑 가격")
    shop0129: int = Field(..., description="cj온스타일 가격")
    shop0154: int = Field(..., description="k쇼핑 가격")
    shop0650: int = Field(..., description="홈&쇼핑 가격")

    # ((기본판매가 + (기본판매가 * 0.05)) 1000자리에서 반올림 후 - 100) + 3000
    shop0029: int = Field(..., description="yes24 가격")
    shop0189: int = Field(..., description="오늘의집 가격")
    shop0322: int = Field(..., description="브랜디 가격")
    shop0444: int = Field(..., description="카카오스타일 가격")
    # ((기본판매가 + (기본판매가 * 0.05)) 1000자리에서 반올림 후 - 100)
    
    shop0100: int = Field(..., description="신세계몰(신) 가격")
    shop0298: int = Field(..., description="cafe24(신) 가격")
    shop0372: int = Field(..., description="롯데온 가격")

    # 기본판매가 + 3000
    shop0381: int = Field(..., description="에이블리 가격")
    shop0416: int = Field(..., description="아트박스(신) 가격")
    shop0449: int = Field(..., description="카카오톡선물하기 가격")
    shop0498: int = Field(..., description="올웨이즈 가격")
    shop0583: int = Field(..., description="토스쇼핑 가격")
    shop0587: int = Field(..., description="aliexpress 가격")
    shop0661: int = Field(..., description="떠리몰 가격")

    # 기본판매가 + 100
    shop0055: int = Field(..., description="스마트스토어 가격")
    shop0067: int = Field(..., description="esm옥션 가격")
    shop0068: int = Field(..., description="esm지마켓 가격")
    shop0273: int = Field(..., description="카카오톡스토어 가격")
    shop0464: int = Field(..., description="11번가 가격")

    # 기본판매가
    shop0075: int = Field(..., description="쿠팡 가격")
    shop0319: int = Field(..., description="도매꾹 가격")
    shop0365: int = Field(..., description="Grip 가격")
    shop0387: int = Field(..., description="하프클럽(신) 가격")