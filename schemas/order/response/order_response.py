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
    

class OrderBulkCreateResponse(BaseModel):
    """
    주문 수집 데이터 대량 DB 저장 응답 객체
    """
    total_count: int = Field(..., description="총 건수")
    success_count: int = Field(..., description="성공 건수")
    duplicated_count: int = Field(..., description="중복값 무시 건수")

class ExcelRunMacroResponse(BaseModel):
    """
    엑셀 매크로 실행 및 업로드 응답 객체
    """
    success: bool = Field(..., description="성공 여부")
    template_code: str = Field(..., description="템플릿 코드")
    batch_id: int | None = Field(None, description="배치 ID")
    file_url: str | None = Field(None, description="업로드 파일 URL")
    object_name: str | None = Field(None, description="Minio 오브젝트명")
    message: str | None = Field(None, description="메시지 또는 에러")

    @classmethod
    def build_success(cls, template_code, batch_id, file_url, object_name):
        datetime_from_url = file_url.split("/")[-1].split("_")[0]
        return cls(
            success=True,
            template_code=template_code,
            batch_id=batch_id,
            file_url=file_url,
            object_name=object_name,
            message=datetime_from_url + " Success"
        )

    @classmethod
    def build_error(cls, template_code, batch_id, message):
        return cls(
            success=False,
            template_code=template_code,
            batch_id=batch_id,
            file_url=None,
            object_name=None,
            message=message
        )
