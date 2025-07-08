from pydantic import BaseModel, Field
from typing import List
from schemas.order.order_dto import OrderDto, OrderBulkDto


class OrderResponse(BaseModel):
    """
    주문 수집 데이터 단건 전송 객체
    """
    order_dto: OrderDto = Field(..., description="주문 수집 데이터 단건")

    @classmethod
    def from_dto(cls, dto: OrderDto) -> "OrderResponse":
        return cls(order_dto=dto)


class OrderResponseList(BaseModel):
    """
    주문 수집 데이터 대량 전송 객체
    """
    success_count: int = Field(..., description="성공 건수")
    error_count: int = Field(..., description="실패 건수")
    success_idx: List[str] = Field(..., description="성공 인덱스")
    errors: List[str] = Field(..., description="실패 에러")
    success_data: List[OrderResponse] = Field(..., description="성공 데이터")

    @classmethod
    def from_dto(cls, dto: OrderBulkDto) -> "OrderResponseList":
        return cls(
            success_count=dto.success_count,
            error_count=dto.error_count,
            success_idx=dto.success_idx,
            errors=dto.errors,
            success_data=[OrderResponse.from_dto(order_dto) for order_dto in dto.success_data],
        )