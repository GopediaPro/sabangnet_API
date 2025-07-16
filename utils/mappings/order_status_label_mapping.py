from enum import Enum


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