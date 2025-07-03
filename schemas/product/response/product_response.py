from pydantic import BaseModel, Field
from datetime import datetime

class ProductNameResponse(BaseModel):
    rev: int = Field(alias="rev", description="수정 차수")
    company_goods_cd: str = Field(alias="company_goods_cd", description="자체상품코드")
    goods_nm: str = Field(alias="goods_nm", description="상품명")

    @classmethod
    def from_dto(cls, dto) -> "ProductNameResponse":
        return cls(
            rev=dto.rev,
            company_goods_cd=dto.compayny_goods_cd,
            goods_nm=dto.goods_nm
        )
    
class ProductResponse(BaseModel):
    goods_nm: str = Field(alias="goods_nm", description="상품명")
    brand_nm: str = Field(alias="brand_nm", description="브랜드명")
    goods_price: int = Field(alias="goods_price", description="상품가격")
    goods_consumer_price: int = Field(alias="goods_consumer_price", description="소비자가격")
    status: str = Field(alias="status", description="상품상태")
    maker: str = Field(alias="maker", description="제조사")
    origin: str = Field(alias="origin", description="원산지")
    goods_keyword: str = Field(alias="goods_keywords", description="상품키워드")
    char_1_nm: str = Field(alias="char_1_nm", description="속성1명")
    char_1_val: str = Field(alias="char_1_val", description="속성1값")
    char_2_nm: str = Field(alias="char_2_nm", description="속성2명")
    char_2_val: str = Field(alias="char_2_val", description="속성2값")
    created_at: datetime = Field(alias="created_at", description="생성일시")

    @classmethod
    def from_dto(cls, dto) -> "ProductResponse":
        return cls(
            goods_nm=dto.goods_nm,
            brand_nm=dto.brand_nm,
            goods_price=dto.goods_price,
            goods_consumer_price=dto.goods_consumer_price,
            status=dto.status,
            maker=dto.maker,
            origin=dto.origin,
            goods_keyword=dto.goods_keyword,
            char_1_nm=dto.char_1_nm,
            char_1_val=dto.char_1_val,
            char_2_nm=dto.char_2_nm,
            char_2_val=dto.char_2_val,
            created_at=dto.created_at
        )