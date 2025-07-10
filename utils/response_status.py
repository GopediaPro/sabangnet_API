from enum import Enum
from typing import Optional, Any, Dict

class RowStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    SKIPPED = "skipped"
    PARTIAL = "partial_success"


def make_row_result(
    id: Optional[Any],
    status: RowStatus,
    message: Optional[str] = None,
    extra: Optional[Dict[str, Any]] = None
) -> dict:
    result = {
        "id": id,
        "status": status.value,
        "message": message
    }
    if extra:
        result.update(extra)
    return result 