from pydantic import BaseModel, Field
from schemas.order.receive_orders_dto import ReceiveOrdersDto, ReceiveOrdersBulkDto


class ReceiveOrdersResponse(BaseModel):
    """
    주문 수집 데이터 단건 전송 객체
    """
    receive_orders_dto: ReceiveOrdersDto = Field(..., description="주문 수집 데이터 단건")

    @classmethod
    def from_dto(cls, dto: ReceiveOrdersDto) -> "ReceiveOrdersResponse":
        return cls(receive_orders_dto=dto)


class ReceiveOrdersResponseList(BaseModel):
    """
    주문 수집 데이터 대량 전송 객체
    """
    success_count: int = Field(..., description="성공 건수")
    error_count: int = Field(..., description="실패 건수")
    success_idx: list[str] = Field(..., description="성공 인덱스")
    errors: list[str] = Field(..., description="실패 에러")
    success_data: list[ReceiveOrdersResponse] = Field(..., description="성공 데이터")

    @classmethod
    def from_dto(cls, dto: ReceiveOrdersBulkDto) -> "ReceiveOrdersResponseList":
        return cls(
            success_count=dto.success_count,
            error_count=dto.error_count,
            success_idx=dto.success_idx,
            errors=dto.errors,
            success_data=[ReceiveOrdersResponse.from_dto(receive_orders_dto) for receive_orders_dto in dto.success_data],
        )
    

class ReceiveOrdersBulkCreateResponse(BaseModel):
    """
    주문 수집 데이터 대량 DB 저장 응답 객체
    """
    total_count: int = Field(..., description="총 건수")
    success_count: int = Field(..., description="성공 건수")
    duplicated_count: int = Field(..., description="중복값 무시 건수")
