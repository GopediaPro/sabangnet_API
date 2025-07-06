from typing import List
from pydantic import BaseModel, Field


class OneOnePriceCreate(BaseModel):
    """1+1 상품 가격 계산을 위한 데이터 단일 생성"""

    product_nm: str = Field(..., description="상품명")
    gubun: str = Field(..., description="구분")

    class Config:
        from_attributes = True


class OneOnePriceBulkCreate(BaseModel):
    """1+1 상품 가격 계산을 위한 데이터 대량 생성"""

    product_nm_and_gubun_list: List[OneOnePriceCreate] = Field(..., description="생성할 상품명 및 구분 리스트")

    class Config:
        from_attributes = True
