from datetime import datetime
from utils.exceptions.order_validation_exceptions import OrderDateRangeException, OrderStatusException


def is_valid_date_from_yyyymmdd(order_date_from_str: str) -> bool:
    # 길이 검사 + 숫자만 포함하는지 확인
    if len(order_date_from_str) != 8 or not order_date_from_str.isdigit():
        raise OrderDateRangeException(f"시작 날짜 형식이 올바르지 않습니다. ({order_date_from_str})")

    # 날짜 형식 유효성 검사 및 datetime 객체 생성
    try:
        date_from = datetime.strptime(order_date_from_str, "%Y%m%d")
    except ValueError:
        raise OrderDateRangeException(f"시작 날짜 형식이 올바르지 않습니다. ({order_date_from_str})")
    
    # 시작일이 오늘 이후인지 확인
    today = datetime.now().date()
    if date_from.date() > today:
        raise OrderDateRangeException(f"시작 날짜가 오늘 이후입니다. ({order_date_from_str})")
    
    return True


def is_valid_date_to_yyyymmdd(order_date_from_str: str, end_date_str: str) -> bool:
    # 길이 검사 + 숫자만 포함하는지 확인
    if len(end_date_str) != 8 or not end_date_str.isdigit():
        raise OrderDateRangeException(f"종료 날짜 형식이 올바르지 않습니다. ({end_date_str})")

    # 날짜 형식 유효성 검사 및 datetime 객체 생성
    try:
        date_to = datetime.strptime(end_date_str, "%Y%m%d")
        date_from = datetime.strptime(order_date_from_str, "%Y%m%d")
    except ValueError:
        raise OrderDateRangeException(f"종료 날짜 형식이 올바르지 않습니다. ({end_date_str})")
    
    # 종료일이 시작일보다 이전인지 확인
    if date_to < date_from:
        raise OrderDateRangeException(f"종료 날짜가 시작 날짜보다 이전입니다. ({end_date_str})")
    
    # 종료일이 오늘 이후인지 확인
    today = datetime.now().date()
    if date_to.date() > today:
        raise OrderDateRangeException(f"종료 날짜가 오늘 이후입니다. ({end_date_str})")
    
    return True


def is_valid_order_status(order_status: str, allow_new_order: bool = False) -> bool:
    """
    만약 001, 002, 003을 사용하고 싶다면 allow_new_order를 True로 설정하세요.
    """
    if order_status in ["001", "002"]:
        if not allow_new_order:
            raise OrderStatusException(f"허용되지 않는 주문 상태입니다. ({order_status})")
        else:
            return True
    elif order_status in ["003", "004", "006", "007", "008", "009", "010", "011", "012", "021", "022", "023", "024", "025", "026", "999"]:
        return True
    else:
        raise OrderStatusException(f"주문 상태 형식이 올바르지 않습니다. ({order_status})")