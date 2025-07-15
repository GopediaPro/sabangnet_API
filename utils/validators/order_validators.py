from datetime import datetime
from utils.exceptions.order_validation_exceptions import OrderDateRangeException, OrderStatusException


def is_start_valid_yyyymmdd(start_date_str: str) -> bool:
    # 길이 검사 + 숫자만 포함하는지 확인
    if len(start_date_str) != 8 or not start_date_str.isdigit():
        raise OrderDateRangeException(f"시작 날짜 형식이 올바르지 않습니다. ({start_date_str})")

    # 날짜 형식 유효성 검사 및 datetime 객체 생성
    try:
        start_date = datetime.strptime(start_date_str, "%Y%m%d")
    except ValueError:
        raise OrderDateRangeException(f"시작 날짜 형식이 올바르지 않습니다. ({start_date_str})")
    
    # 시작일이 오늘 이후인지 확인
    today = datetime.now().date()
    if start_date.date() > today:
        raise OrderDateRangeException(f"시작 날짜가 오늘 이후입니다. ({start_date_str})")
    
    return True


def is_end_valid_yyyymmdd(start_date_str: str, end_date_str: str) -> bool:
    # 길이 검사 + 숫자만 포함하는지 확인
    if len(end_date_str) != 8 or not end_date_str.isdigit():
        raise OrderDateRangeException(f"종료 날짜 형식이 올바르지 않습니다. ({end_date_str})")

    # 날짜 형식 유효성 검사 및 datetime 객체 생성
    try:
        end_date = datetime.strptime(end_date_str, "%Y%m%d")
        start_date = datetime.strptime(start_date_str, "%Y%m%d")
    except ValueError:
        raise OrderDateRangeException(f"종료 날짜 형식이 올바르지 않습니다. ({end_date_str})")
    
    # 종료일이 시작일보다 이전인지 확인
    if end_date < start_date:
        raise OrderDateRangeException(f"종료 날짜가 시작 날짜보다 이전입니다. ({end_date_str})")
    
    # 종료일이 오늘 이후인지 확인
    today = datetime.now().date()
    if end_date.date() > today:
        raise OrderDateRangeException(f"종료 날짜가 오늘 이후입니다. ({end_date_str})")
    
    return True


def is_valid_order_status(order_status: str, allow_new_order: bool = False) -> bool:
    """
    만약 001, 002, 003을 사용하고 싶다면 allow_new_order를 True로 설정하세요.
    """
    if order_status in ["001", "002", "003"]:
        if not allow_new_order:
            raise OrderStatusException(f"허용되지 않는 주문 상태입니다. ({order_status})")
        else:
            return True
    elif order_status in ["004", "006", "007", "008", "009", "010", "011", "012", "021", "022", "023", "024", "025", "026", "999"]:
        return True
    else:
        raise OrderStatusException(f"주문 상태 형식이 올바르지 않습니다. ({order_status})")