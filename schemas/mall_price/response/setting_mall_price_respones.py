from pydantic import BaseModel, Field
from schemas.mall_price.mall_price_dto import MallPriceDto

class SettingMallPriceResponse(BaseModel):
    standard_price: int = Field(..., description="기준 가격(기본판매가)")

    # ((기본판매가 + (기본판매가 * 0.15)) 1000자리에서 반올림 후 - 100) + 3000
    gs_shop_price: int = Field(..., description="GS SHOP 판매가")            # shop0007
    # ((기본판매가 + (기본판매가 * 0.05)) 1000자리에서 반올림 후 - 100) + 3000
    yes24_price: int = Field(..., description="YES24 판매가")               # shop0029
    # ((기본판매가 + (기본판매가 * 0.05)) 1000자리에서 반올림 후 - 100)
    ssgmall_price: int = Field(..., description="신세계몰 판매가")           # shop0100
    # 기본판매가 + 3000
    ably_price: int = Field(..., description="에이블리 판매가")              # shop0381
    # 기본판매가 + 100
    smartstore_price: int = Field(..., description="네이버 스마트스토어 판매가")  # shop0055
    # 기본판매가
    coupang_price: int = Field(..., description="쿠팡 판매가")               # shop0075
    
    @classmethod
    def from_dto(cls, dto: MallPriceDto) -> "SettingMallPriceResponse":
        return cls(
            standard_price=dto.standard_price,
            gs_shop_price=dto.shop0007,
            yes24_price=dto.shop0029,
            ssgmall_price=dto.shop0100,
            ably_price=dto.shop0381,
            smartstore_price=dto.shop0055,
            coupang_price=dto.shop0075,
        )