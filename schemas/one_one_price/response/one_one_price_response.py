from decimal import Decimal
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_serializer
from models.one_one_price.one_one_price import OneOnePrice
from schemas.one_one_price.one_one_price_dto import OneOnePriceDto, OneOnePriceBulkDto


class OneOnePriceResponse(BaseModel):

    """1+1 상품 가격 계산을 위한 데이터 응답"""

    group_115: Decimal = Field(..., description="1+1 115% 가격")
    group_105: Decimal = Field(..., description="1+1 105% 가격")
    group_same: Decimal = Field(..., description="1+1 기본 가격")
    group_plus100: Decimal = Field(..., description="1+1 + 100 가격")
    created_at: Optional[datetime] = Field(None, description="생성일시")

    @field_serializer("group_115", "group_105", "group_same", "group_plus100")
    def serialize_decimal(self, v: Decimal, _info):
        return float(v)

    @classmethod
    def from_dto(cls, dto: OneOnePriceDto) -> "OneOnePriceResponse":
        """DTO에서 Response 객체 생성"""
        data = {}
        # DTO 데이터를 복사하고 추가 필드 설정
        data["group_115"] = dto.shop0007
        data["group_105"] = dto.shop0029
        data["group_same"] = dto.shop0381
        data["group_plus100"] = dto.shop0055
        data["created_at"] = datetime.now()
        return cls(**data)

    @classmethod
    def from_model(cls, model: OneOnePrice) -> "OneOnePriceResponse":
        """DB 모델에서 Response 객체 생성"""
        return cls.model_validate(model)


class OneOnePriceBulkResponse(BaseModel):
    """1+1 상품 가격 계산을 위한 데이터 대량 처리 응답"""

    success_count: int = Field(..., description="성공한 데이터 수")
    error_count: int = Field(..., description="실패한 데이터 수")
    created_product_nm: List[str] = Field(..., description="계산된 상품명 리스트")
    errors: List[str] = Field(default_factory=list, description="오류 메시지 리스트")
    success_data: List[OneOnePriceResponse] = Field(
        default_factory=list, description="성공적으로 생성된 데이터"
    )

    class Config:
        from_attributes = True

    @classmethod
    def from_dto(cls, dto: OneOnePriceBulkDto) -> "OneOnePriceBulkResponse":
        return cls(
            success_count=dto.success_count,
            error_count=dto.error_count,
            created_product_nm=dto.created_product_nm,
            errors=dto.errors,
            success_data=[OneOnePriceResponse.from_dto(dto) for dto in dto.success_data],
        )