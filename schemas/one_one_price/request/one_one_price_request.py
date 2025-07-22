from pydantic import BaseModel, Field


class OneOnePriceCreate(BaseModel):
    """1+1 상품 가격 계산을 위한 데이터 단일 생성"""

    product_nm: str = Field(..., description="상품명")
    gubun: str = Field(..., description="구분")

    class Config:
        from_attributes = True


class OneOnePriceBulkCreate(BaseModel):
    product_nm_and_gubun_list: list[OneOnePriceCreate]

    def to_dto(self) -> list[OneOnePriceCreate]:
        return self.product_nm_and_gubun_list
