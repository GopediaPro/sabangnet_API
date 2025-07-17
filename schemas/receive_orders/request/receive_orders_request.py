from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from utils.validators.order_validators import is_start_valid_yyyymmdd, is_end_valid_yyyymmdd, is_valid_order_status
from utils.mappings.order_status_label_mapping import STATUS_LABEL_TO_CODE, OrderStatusLabel, OrderStatus


class BaseDateRangeRequest(BaseModel):
    """
    기간 필터 요청 객체 - 모든 필드 Optional
    """
    date_from: Optional[date] = Field(None, description="시작 날짜", example="2025-06-02")
    date_to: Optional[date] = Field(None, description="종료 날짜", example="2025-06-06")

    @field_validator("date_from")
    @classmethod
    def validate_order_date_from(cls, date_from: Optional[date]) -> Optional[date]:
        if date_from is None:
            return None
        # YYYYMMDD 형식으로 변환 후 검증
        order_date_from_str = date_from.strftime('%Y%m%d')
        is_start_valid_yyyymmdd(order_date_from_str)
        return date_from
    
    @model_validator(mode='after')
    def validate_date_range(self):
        # 둘 다 None이면 검증 스킵
        if self.date_from is None or self.date_to is None:
            return self
        # YYYYMMDD 형식으로 변환 후 검증
        order_date_from_str = self.date_from.strftime('%Y%m%d')
        end_date_str = self.date_to.strftime('%Y%m%d')
        is_end_valid_yyyymmdd(order_date_from_str, end_date_str)
        return self
    
    def get_order_date_from_yyyymmdd(self) -> Optional[str]:
        """시작 날짜를 YYYYMMDD 형식으로 반환"""
        return self.date_from.strftime('%Y%m%d') if self.date_from else None
    
    def get_end_date_yyyymmdd(self) -> Optional[str]:
        """종료 날짜를 YYYYMMDD 형식으로 반환"""
        return self.date_to.strftime('%Y%m%d') if self.date_to else None


class ReceiveOrdersRequest(BaseDateRangeRequest):
    """
    날짜/주문상태 필수 요청 객체
    """
    # 부모 클래스의 Optional 필드들을 필수로 오버라이드
    date_from: date = Field(default=date(2025, 6, 2), description="시작 날짜", example="2025-06-02")
    date_to: date = Field(default=date(2025, 6, 6), description="종료 날짜", example="2025-06-06")
    
    order_status: OrderStatusLabel = Field(
        default=OrderStatusLabel.SHIPMENT_COMPLETED,
        example=OrderStatusLabel.SHIPMENT_COMPLETED.value,
        description="""
            주문 상태
            --------------------------------
            신규주문 (사용주의)
            주문확인 (사용주의)
            출고대기 (사용주의)
            출고완료
            배송보류
            취소접수
            교환접수
            반품접수
            취소완료
            교환완료
            반품완료
            교환발송준비
            교환발송완료
            교환회수준비
            교환회수완료
            반품회수준비
            반품회수완료
            폐기
            --------------------------------
        """
    )

    @field_validator("order_status")
    @classmethod
    def validate_order_status(cls, order_status: OrderStatusLabel) -> OrderStatusLabel:
        # 한글 라벨을 코드로 변환하여 기존 validator에 전달
        order_code = STATUS_LABEL_TO_CODE[order_status]
        is_valid_order_status(order_code.value)
        return order_status
    
    def get_order_status_code(self) -> str:
        """주문 상태의 코드값을 반환"""
        return STATUS_LABEL_TO_CODE[self.order_status].value

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "date_from": "2025-06-02",
                "date_to": "2025-06-06", 
                "order_status": "출고완료"
            }
        }
    )


class ReceiveOrdersFillterRequest(BaseDateRangeRequest):
    """
    날짜/주문상태 Optional 요청 객체
    """
    # 부모 클래스가 이미 모든 필드를 Optional로 제공하므로 그대로 사용
    mall_id: Optional[str] = Field(None, description="몰 ID")
    order_status: Optional[OrderStatusLabel] = Field(None, description="주문 상태")
    
    @field_validator("order_status")
    @classmethod
    def validate_order_status_optional(cls, order_status: Optional[OrderStatusLabel]) -> Optional[OrderStatusLabel]:
        if order_status is None:
            return None
        # 한글 라벨을 코드로 변환하여 기존 validator에 전달
        order_code = STATUS_LABEL_TO_CODE[order_status]
        is_valid_order_status(order_code.value)
        return order_status

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "date_from": "2025-06-02",
                "date_to": "2025-06-06",
                "order_status": "출고완료",
                "mall_id": "ESM지마켓"
            }
        }
    )