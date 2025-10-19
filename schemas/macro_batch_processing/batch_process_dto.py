from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class BatchProcessDto(BaseModel):
    batch_id: Optional[int] = Field(None, description="배치 프로세스 고유 ID")
    original_filename: Optional[str] = Field(None, description="원본 파일 이름")
    file_name: Optional[str] = Field(None, description="배치 파일 이름")
    file_url: Optional[str] = Field(None, description="배치 파일 URL")
    file_size: Optional[int] = Field(None, description="배치 파일 크기")
    date_from: Optional[datetime] = Field(None, description="주문 시작 일자")
    date_to: Optional[datetime] = Field(None, description="주문 종료 일자")
    error_message: Optional[str] = Field(None, description="배치 프로세스 오류 메시지")
    created_by: Optional[str] = Field(None, description="배치 프로세스 생성자 ID")
    work_status: Optional[str] = Field(None, description="작업 상태")
    target_table: Optional[str] = Field(None, description="처리 대상 테이블명")
    target_table_ids: Optional[List[int]] = Field(None, description="처리 대상 테이블 레코드 ID 배열")
    batch_name: Optional[str] = Field(None, description="배치 프로세스 이름")
    file_hash: Optional[str] = Field(None, description="배치 파일 해시 (무결성 검증용)")
    total_records: Optional[int] = Field(None, description="처리 대상 레코드 수")
    success_records: Optional[int] = Field(None, description="성공 레코드 수")
    fail_records: Optional[int] = Field(None, description="실패 레코드 수")
    skip_records: Optional[int] = Field(None, description="건너뛴 레코드 수")
    created_at: Optional[datetime] = Field(None, description="배치 프로세스 생성 일자")
    updated_at: Optional[datetime] = Field(None, description="배치 프로세스 수정 일자")

    class Config:
        from_attributes = True

    @classmethod
    def build_success(cls, original_filename: str, file_url: str, file_size: int, request_obj) -> 'BatchProcessDto':
        """
        성공적인 배치 처리를 위한 DTO 생성
        """
        return cls(
            original_filename=original_filename,
            file_url=file_url,
            file_size=file_size,
            work_status="success",
            created_by=getattr(request_obj, 'created_by', 'system'),
            date_from=getattr(request_obj.filters, 'date_from', None) if hasattr(request_obj, 'filters') and request_obj.filters else None,
            date_to=getattr(request_obj.filters, 'date_to', None) if hasattr(request_obj, 'filters') and request_obj.filters else None
        )

    @classmethod
    def build_error(cls, original_filename: str, request_obj, error_message: str) -> 'BatchProcessDto':
        """
        에러가 발생한 배치 처리를 위한 DTO 생성
        """
        return cls(
            original_filename=original_filename,
            error_message=error_message,
            work_status="error",
            created_by=getattr(request_obj, 'created_by', 'system'),
            date_from=getattr(request_obj.filters, 'date_from', None) if hasattr(request_obj, 'filters') and request_obj.filters else None,
            date_to=getattr(request_obj.filters, 'date_to', None) if hasattr(request_obj, 'filters') and request_obj.filters else None
        )

    @classmethod
    def build_success_with_status(cls, original_filename: str, file_url: str, file_size: int, request_obj, work_status: str) -> 'BatchProcessDto':
        """
        특정 작업 상태로 성공적인 배치 처리를 위한 DTO 생성
        """
        return cls(
            original_filename=original_filename,
            file_url=file_url,
            file_size=file_size,
            work_status=work_status,
            created_by=getattr(request_obj, 'created_by', 'system'),
            date_from=getattr(request_obj.filters, 'date_from', None) if hasattr(request_obj, 'filters') and request_obj.filters else None,
            date_to=getattr(request_obj.filters, 'date_to', None) if hasattr(request_obj, 'filters') and request_obj.filters else None
        )