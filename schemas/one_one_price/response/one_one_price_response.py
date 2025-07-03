from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from schemas.one_one_price.one_one_price_dto import OneOnePriceDto


class OneOnePriceResponse(OneOnePriceDto):
    """1+1 상품 가격 계산을 위한 데이터 응답"""

    id: int = Field(..., description="고유 식별자")
    created_at: Optional[datetime] = Field(None, description="생성일시")
    updated_at: Optional[datetime] = Field(None, description="수정일시")

    @classmethod
    def from_dto(cls, dto: OneOnePriceDto) -> "OneOnePriceResponse":
        """DTO에서 Response 객체 생성"""
        # DTO 데이터를 복사하고 추가 필드 설정
        data = dto.model_dump()
        data["id"] = dto.product_registration_raw_data_id
        data["created_at"] = datetime.now()
        data["updated_at"] = datetime.now()
        return cls(**data)

    @classmethod
    def from_model(cls, model) -> "OneOnePriceResponse":
        """DB 모델에서 Response 객체 생성"""
        return cls.model_validate(model)


class OneOnePriceBulkResponse(BaseModel):
    """1+1 상품 가격 계산을 위한 데이터 대량 처리 응답"""

    success_count: int = Field(..., description="성공한 데이터 수")
    error_count: int = Field(..., description="실패한 데이터 수")
    created_ids: List[int] = Field(..., description="생성된 데이터 ID 리스트")
    errors: List[str] = Field(default_factory=list, description="오류 메시지 리스트")
    success_data: List[OneOnePriceResponse] = Field(
        default_factory=list, description="성공적으로 생성된 데이터"
    )

    class Config:
        from_attributes = True

    @classmethod
    def from_dto(cls, dto: OneOnePriceDto) -> "OneOnePriceResponse":
        return cls(**dto.model_dump())