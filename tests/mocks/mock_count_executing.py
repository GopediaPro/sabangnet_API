from typing import Any
from datetime import datetime


COUNT_EXECUTING: list[dict[str, Any]] = [
    {
        "id": 1,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "count_nm": "상품등록_프로세스",
        "count_rev": 1,
    },
    {
        "id": 2,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "count_nm": "주문처리_프로세스",
        "count_rev": 2,
    }
]