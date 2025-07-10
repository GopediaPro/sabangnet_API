"""
주문 수집 데이터 유효성 검사 예외 클래스
"""


class OrderDateRangeException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class OrderStatusException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)