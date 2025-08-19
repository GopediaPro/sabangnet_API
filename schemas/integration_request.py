from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Optional, TypeVar, Generic


# 제네릭 타입 변수 정의
T = TypeVar('T')


class Metadata(BaseModel):
    request_id: Optional[str] = Field(None, description="요청 ID")


class IntegrationRequest(BaseModel, Generic[T]):
    data: T = Field(..., description="데이터")
    metadata: Metadata = Field(..., description="메타데이터")
