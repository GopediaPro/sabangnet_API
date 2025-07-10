from enum import Enum
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


class OrderXmlTemplateRequest(BaseModel):
    start_date: str = Field(
        description="시작 날짜 (YYYYMMDD 형식)",
        example="20250602",
        default="20250602"
    )
    end_date: str = Field(
        description="종료 날짜 (YYYYMMDD 형식)",
        example="20250606",
        default="20250606"
    )
    order_status: OrderStatus = Field(
        default=OrderStatus.SHIPMENT_COMPLETED,
        example=OrderStatus.SHIPMENT_COMPLETED.value,
        description="""
            주문 상태
            --------------------------------
            001: 신규주문(사용주의)
            002: 주문확인(사용주의)
            003: 출고대기(사용주의)
            004: 출고완료
            006: 배송보류
            007: 취소접수
            008: 교환접수
            009: 반품접수
            010: 취소완료
            011: 교환완료
            012: 반품완료
            021: 교환발송준비
            022: 교환발송완료
            023: 교환회수준비
            024: 교환회수완료
            025: 반품회수준비
            026: 반품회수완료
            999: 폐기
            --------------------------------
        """
    )

    @field_validator("start_date")
    @classmethod
    def validate_start_date(cls, start_date: str) -> str:
        is_start_valid_yyyymmdd(start_date)
        return start_date
    
    @field_validator("order_status")
    @classmethod
    def validate_order_status(cls, order_status: OrderStatus) -> OrderStatus:
        is_valid_order_status(order_status.value)
        return order_status

    @model_validator(mode='after')
    def validate_date_range(self):
        is_end_valid_yyyymmdd(self.start_date, self.end_date)
        return self

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "start_date": "20250602",
                "end_date": "20250606", 
                "order_status": "004"  # 출고완료
            }
        }
    )