from pydantic import BaseModel, Field


class DownFormOrderCreate(BaseModel):
    """다운폼 주문 생성 DTO"""

    idx: str = Field(..., description="사방넷주문번호")


class DownFormOrderRead(BaseModel):
    """다운폼 주문 읽기 DTO"""

    idx: str = Field(..., description="사방넷주문번호")
