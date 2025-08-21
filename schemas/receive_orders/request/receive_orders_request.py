from datetime import date
from typing import Optional, Union
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from utils.mappings.order_status_label_mapping import STATUS_LABEL_TO_CODE, OrderStatusLabel
from utils.validators.order_validators import is_valid_date_from_yyyymmdd, is_valid_date_to_yyyymmdd, is_valid_order_status


class BaseDateRangeRequest(BaseModel):
    """
    기간 필터 요청 객체 - 모든 필드 Optional
    """
    date_from: Optional[date] = Field(
        None, description="시작 날짜", example="2025-06-02")
    date_to: Optional[date] = Field(
        None, description="종료 날짜", example="2025-06-06")

    @field_validator("date_from", mode='before')
    @classmethod
    def validate_order_date_from(cls, date_from: Optional[Union[date, str]]) -> Optional[date]:
        if date_from is None:
            return None

        if isinstance(date_from, str):
            """
            프론트에서 문자열로 요청이 오는 경우 date 객체로 변환해줌
            """
            try:
                date_from = date.fromisoformat(date_from)
            except ValueError:
                raise ValueError(f"시작 날짜 형식이 올바르지 않습니다. ({date_from})")
        elif isinstance(date_from, date):
            """
            프론트에서 date 객체로 요청이 오는 경우 그대로 반환
            """
            pass
        else:
            raise ValueError(f"시작 날짜는 str 또는 date 객체여야 합니다. ({date_from})")

        # YYYYMMDD 형식으로 변환 후 검증
        order_date_from_str = date_from.strftime('%Y%m%d')
        is_valid_date_from_yyyymmdd(order_date_from_str)
        return date_from

    @field_validator("date_to", mode='before')
    @classmethod
    def validate_date_to(cls, date_to: Optional[Union[date, str]]) -> Optional[date]:
        if date_to is None:
            return None

        # 문자열인 경우 date 객체로 변환
        if isinstance(date_to, str):
            try:
                date_to = date.fromisoformat(date_to)
            except ValueError:
                raise ValueError(f"종료날짜 형식이 올바르지 않습니다. ({date_to})")
        elif isinstance(date_to, date):
            """
            프론트에서 date 객체로 요청이 오는 경우 그대로 반환
            """
            pass
        else:
            raise ValueError(f"종료날짜는 str 또는 date 객체여야 합니다. ({date_to})")

        return date_to

    @model_validator(mode='after')
    def validate_date_range(self):
        # 둘 다 None이면 검증 스킵
        if self.date_from is None or self.date_to is None:
            return self
        # YYYYMMDD 형식으로 변환 후 검증
        order_date_from_str = self.date_from.strftime('%Y%m%d')
        end_date_str = self.date_to.strftime('%Y%m%d')
        is_valid_date_to_yyyymmdd(order_date_from_str, end_date_str)
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
    date_from: date = Field(..., description="시작 날짜", example="2025-06-02")
    date_to: date = Field(..., description="종료 날짜", example="2025-06-06")

    order_status: OrderStatusLabel = Field(
        ...,
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

    @field_validator("order_status", mode='before')
    @classmethod
    def validate_order_status_required(cls, order_status: Optional[Union[OrderStatusLabel, str]]) -> Optional[OrderStatusLabel]:
        # 문자열인 경우 OrderStatusLabel enum으로 변환 (프론트엔드에서 오는 경우)
        if isinstance(order_status, str):
            try:
                order_status = OrderStatusLabel(order_status)
            except ValueError:
                raise ValueError(f"주문 상태 형식이 올바르지 않습니다. {order_status}")
        elif isinstance(order_status, OrderStatusLabel):
            pass
        else:
            raise ValueError(
                f"주문 상태는 str 또는 OrderStatusLabel이어야 합니다. ({order_status})")

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


class ReceiveOrdersToDownFormOrdersFillterRequst(ReceiveOrdersFillterRequest):
    dpartner_id: Optional[str] = Field(..., description="배송구분(일반배송, 스타배송)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "date_from": "2025-06-02",
                "date_to": "2025-06-06",
                "order_status": "출고완료",
                "mall_id": "ESM지마켓",
                "dpartner_id": "오케이마트"
            }
        }
    )
