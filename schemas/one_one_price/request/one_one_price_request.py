from pydantic import BaseModel, Field, RootModel


class OneOnePriceCreate(BaseModel):
    """1+1 상품 가격 계산을 위한 데이터 단일 생성"""

    product_nm: str = Field(..., description="상품명")
    gubun: str = Field(..., description="구분")

    class Config:
        from_attributes = True


class OneOnePriceBulkCreate(RootModel[dict[str, OneOnePriceCreate]]):
    """1+1 상품 가격 계산을 위한 데이터 대량 생성"""

    def to_dto(self) -> list[OneOnePriceCreate]:
        """Dict 데이터를 DTO로 변환"""

        # 이렇게 나옴 -> [{"product_nm": "상품명1", "gubun": "구분1"}, {"product_nm": "상품명2", "gubun": "구분2"} ... ]
        return list(self.root.values())
