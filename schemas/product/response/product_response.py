from pydantic import BaseModel, Field

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