from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

# BaseDTO 정의 (없으면 추가)
class BaseDTO(BaseModel):
    def to_orm(self, orm_class):
        # DTO의 dict에서 ORM 모델의 필드만 추출
        orm_fields = {k: v for k, v in self.model_dump(exclude_unset=True).items() if k in orm_class.__table__.columns}
        return orm_class(**orm_fields)


class BatchProcessDto(BaseDTO):
    """
    배치 프로세스 DTO (DB 스키마와 1:1 매핑)
    """
    batch_id: Optional[int] = Field(None, description="배치 프로세스 ID")
    original_filename: Optional[str] = Field(None, description="원본 파일명")
    file_name: Optional[str] = Field(None, description="파일명")
    file_url: Optional[str] = Field(None, description="파일 URL")
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

    @classmethod
    def build_success(cls, original_filename, file_url, file_size, request):
        file_name = file_url.split("/")[-1] if file_url else None
        return cls(
            original_filename=original_filename,
            file_name=file_name,
            file_url=file_url,
            file_size=file_size,
            order_date_from=getattr(request, 'filters', None).order_date_from if getattr(request, 'filters', None) else None,
            order_date_to=getattr(request, 'filters', None).order_date_to if getattr(request, 'filters', None) else None,
            created_by=getattr(request, 'created_by', None)
        )

    @classmethod
    def build_error(cls, original_filename, request, error_message):
        return cls(
            original_filename=original_filename,
            file_name=None,
            file_url=None,
            file_size=None,
            error_message=error_message,
            order_date_from=getattr(request, 'filters', None).order_date_from if getattr(request, 'filters', None) else None,
            order_date_to=getattr(request, 'filters', None).order_date_to if getattr(request, 'filters', None) else None,
            created_by=getattr(request, 'created_by', None)
        )