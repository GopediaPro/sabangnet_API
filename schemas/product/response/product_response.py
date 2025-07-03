from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

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
    id: int = Field(alias="id", description="ID")
    goods_nm: str = Field(alias="goods_nm", description="상품명")
    brand_nm: str = Field(alias="brand_nm", description="브랜드명")
    goods_price: int = Field(alias="goods_price", description="상품가격")
    goods_consumer_price: int = Field(alias="goods_consumer_price", description="소비자가격")
    status: int = Field(alias="status", description="상품상태")
    maker: str = Field(alias="maker", description="제조사")
    origin: str = Field(alias="origin", description="원산지")
    goods_keyword: str = Field(alias="goods_keyword", description="상품키워드")
    char_1_nm: Optional[str] = Field(alias="char_1_nm", default=None, description="속성1명")
    char_1_val: Optional[str] = Field(alias="char_1_val", default=None, description="속성1값")
    char_2_nm: Optional[str] = Field(alias="char_2_nm", default=None, description="속성2명")
    char_2_val: Optional[str] = Field(alias="char_2_val", default=None, description="속성2값")
    created_at: datetime = Field(alias="created_at", description="생성일시")

    @classmethod
    def from_dto(cls, dto) -> "ProductResponse":
        return cls(
            id=dto.id,
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
    
class ProductPageResponse(BaseModel):
    products: list[ProductResponse] = Field(description="상품 목록")
    current_page: int = Field(description="현재 페이지")
    page_size: int = Field(description="페이지 크기")

    @classmethod
    def builder(cls, products: list[ProductResponse], current_page: int, page_size: int) -> "ProductPageResponse":
        return cls(
            products=products,
            current_page=current_page,
            page_size=page_size
        )
