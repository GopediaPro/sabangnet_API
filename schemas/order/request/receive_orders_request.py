from enum import Enum
from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from utils.validators.order_validators import is_start_valid_yyyymmdd, is_end_valid_yyyymmdd, is_valid_order_status


class OrderStatus(str, Enum):
    """
    상태코드 타입

    001: 신규주문(사용주의)\n
    002: 주문확인(사용주의)\n
    003: 출고대기(사용주의)\n
    004: 출고완료\n
    006: 배송보류\n
    007: 취소접수\n
    008: 교환접수\n
    009: 반품접수\n
    010: 취소완료\n
    011: 교환완료\n
    012: 반품완료\n
    021: 교환발송준비\n
    022: 교환발송완료\n
    023: 교환회수준비\n
    024: 교환회수완료\n
    025: 반품회수준비\n
    026: 반품회수완료\n
    999: 폐기
    """

    NEW_ORDER = "001"
    ORDER_CONFIRMATION = "002"
    READY_FOR_SHIPMENT = "003"
    SHIPMENT_COMPLETED = "004"
    SHIPMENT_ON_HOLD = "006"
    CANCEL_RECEIVED = "007"
    EXCHANGE_RECEIVED = "008"
    RETURN_RECEIVED = "009"
    CANCEL_COMPLETED = "010"
    EXCHANGE_COMPLETED = "011"
    RETURN_COMPLETED = "012"
    EXCHANGE_SHIPMENT_READY = "021"
    EXCHANGE_SHIPMENT_COMPLETED = "022"
    EXCHANGE_RECEIVE_READY = "023"
    EXCHANGE_RECEIVE_COMPLETED = "024"
    RETURN_RECEIVE_READY = "025"
    RETURN_RECEIVE_COMPLETED = "026"
    DISCARD = "999"


class OrderStatusLabel(str, Enum):
    """
    사용자 친화적인 주문 상태 라벨
    """
    NEW_ORDER = "신규주문"
    ORDER_CONFIRMATION = "주문확인"
    READY_FOR_SHIPMENT = "출고대기"
    SHIPMENT_COMPLETED = "출고완료"
    SHIPMENT_ON_HOLD = "배송보류"
    CANCEL_RECEIVED = "취소접수"
    EXCHANGE_RECEIVED = "교환접수"
    RETURN_RECEIVED = "반품접수"
    CANCEL_COMPLETED = "취소완료"
    EXCHANGE_COMPLETED = "교환완료"
    RETURN_COMPLETED = "반품완료"
    EXCHANGE_SHIPMENT_READY = "교환발송준비"
    EXCHANGE_SHIPMENT_COMPLETED = "교환발송완료"
    EXCHANGE_RECEIVE_READY = "교환회수준비"
    EXCHANGE_RECEIVE_COMPLETED = "교환회수완료"
    RETURN_RECEIVE_READY = "반품회수준비"
    RETURN_RECEIVE_COMPLETED = "반품회수완료"
    DISCARD = "폐기"


# 한글 라벨을 상태 코드로 매핑하는 딕셔너리
STATUS_LABEL_TO_CODE = {
    OrderStatusLabel.NEW_ORDER: OrderStatus.NEW_ORDER,
    OrderStatusLabel.ORDER_CONFIRMATION: OrderStatus.ORDER_CONFIRMATION,
    OrderStatusLabel.READY_FOR_SHIPMENT: OrderStatus.READY_FOR_SHIPMENT,
    OrderStatusLabel.SHIPMENT_COMPLETED: OrderStatus.SHIPMENT_COMPLETED,
    OrderStatusLabel.SHIPMENT_ON_HOLD: OrderStatus.SHIPMENT_ON_HOLD,
    OrderStatusLabel.CANCEL_RECEIVED: OrderStatus.CANCEL_RECEIVED,
    OrderStatusLabel.EXCHANGE_RECEIVED: OrderStatus.EXCHANGE_RECEIVED,
    OrderStatusLabel.RETURN_RECEIVED: OrderStatus.RETURN_RECEIVED,
    OrderStatusLabel.CANCEL_COMPLETED: OrderStatus.CANCEL_COMPLETED,
    OrderStatusLabel.EXCHANGE_COMPLETED: OrderStatus.EXCHANGE_COMPLETED,
    OrderStatusLabel.RETURN_COMPLETED: OrderStatus.RETURN_COMPLETED,
    OrderStatusLabel.EXCHANGE_SHIPMENT_READY: OrderStatus.EXCHANGE_SHIPMENT_READY,
    OrderStatusLabel.EXCHANGE_SHIPMENT_COMPLETED: OrderStatus.EXCHANGE_SHIPMENT_COMPLETED,
    OrderStatusLabel.EXCHANGE_RECEIVE_READY: OrderStatus.EXCHANGE_RECEIVE_READY,
    OrderStatusLabel.EXCHANGE_RECEIVE_COMPLETED: OrderStatus.EXCHANGE_RECEIVE_COMPLETED,
    OrderStatusLabel.RETURN_RECEIVE_READY: OrderStatus.RETURN_RECEIVE_READY,
    OrderStatusLabel.RETURN_RECEIVE_COMPLETED: OrderStatus.RETURN_RECEIVE_COMPLETED,
    OrderStatusLabel.DISCARD: OrderStatus.DISCARD,
}


class ReceiveOrdersRequest(BaseModel):
    start_date: date = Field(
        default=date(2025, 6, 2),
        description="시작 날짜",
        example="2025-06-02"
    )
    end_date: date = Field(
        default=date(2025, 6, 6),
        description="종료 날짜",
        example="2025-06-06"
    )
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

    @field_validator("start_date")
    @classmethod
    def validate_start_date(cls, start_date: date) -> date:
        # 기존 validator 호환을 위해 YYYYMMDD 형식으로 변환 후 검증
        start_date_str = start_date.strftime('%Y%m%d')
        is_start_valid_yyyymmdd(start_date_str)
        return start_date
    
    @field_validator("order_status")
    @classmethod
    def validate_order_status(cls, order_status: OrderStatusLabel) -> OrderStatusLabel:
        # 한글 라벨을 코드로 변환하여 기존 validator에 전달
        order_code = STATUS_LABEL_TO_CODE[order_status]
        is_valid_order_status(order_code.value)
        return order_status

    @model_validator(mode='after')
    def validate_date_range(self):
        # 기존 validator 호환을 위해 YYYYMMDD 형식으로 변환 후 검증
        start_date_str = self.start_date.strftime('%Y%m%d')
        end_date_str = self.end_date.strftime('%Y%m%d')
        is_end_valid_yyyymmdd(start_date_str, end_date_str)
        return self
    
    def get_start_date_yyyymmdd(self) -> str:
        """시작 날짜를 YYYYMMDD 형식으로 반환"""
        return self.start_date.strftime('%Y%m%d')
    
    def get_end_date_yyyymmdd(self) -> str:
        """종료 날짜를 YYYYMMDD 형식으로 반환"""
        return self.end_date.strftime('%Y%m%d')
    
    def get_order_status_code(self) -> str:
        """주문 상태의 코드값을 반환"""
        return STATUS_LABEL_TO_CODE[self.order_status].value

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "start_date": "2025-06-02",
                "end_date": "2025-06-06", 
                "order_status": "출고완료"
            }
        }
    )


class ReceiveOrdersFillterRequest(ReceiveOrdersRequest):
    # 부모 클래스 필드들을 Optional로 오버라이드 했음
    start_date: Optional[date] = Field(None, description="시작 날짜")
    end_date: Optional[date] = Field(None, description="종료 날짜") 
    order_status: Optional[OrderStatusLabel] = Field(None, description="주문 상태")
    
    # 몰아이디 필드 추가
    mall_id: str = Field(..., description="몰 ID")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "start_date": "2025-06-02",
                "end_date": "2025-06-06",
                "order_status": "출고완료",
                "mall_id": "ESM지마켓"
            }
        }
    )