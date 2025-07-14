from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

# BaseDTO 정의 (없으면 추가)
class BaseDTO(BaseModel):
    def to_orm(self, orm_class):
        return orm_class(**self.model_dump())


class BatchProcessDto(BaseDTO):
    """
    배치 프로세스 DTO (DB 스키마와 1:1 매핑)
    """
    batch_id: Optional[int] = Field(None, description="배치 프로세스 ID")
    original_filename: Optional[str] = Field(None, description="원본 파일명")
    file_name: Optional[str] = Field(None, description="파일명")
    file_path: Optional[str] = Field(None, description="파일 경로")
    file_size: Optional[int] = Field(None, description="파일 크기")
    order_date_from: Optional[datetime] = Field(None, description="주문 일자 시작")
    order_date_to: Optional[datetime] = Field(None, description="주문 일자 종료")
    order_status: Optional[str] = Field(None, description="주문 상태")
    error_message: Optional[str] = Field(None, description="에러 메시지")
    created_by: Optional[str] = Field(None, description="생성자")
    created_at: Optional[datetime] = Field(None, description="생성 일시")
    updated_at: Optional[datetime] = Field(None, description="수정 일시")

    model_config = ConfigDict(
        from_attributes=True,
    )