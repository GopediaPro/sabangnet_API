from datetime import datetime
from models.base_model import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime, Text, BigInteger


class BatchProcess(Base):
    """
    배치 프로세스 테이블(batch_process)의 ORM 매핑 모델
    """

    __tablename__ = "batch_process"

    batch_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True,comment="배치 프로세스 고유 ID")
    original_filename: Mapped[str | None] = mapped_column(String(255),comment="원본 파일 이름")
    file_name: Mapped[str | None] = mapped_column(Text, comment="배치 파일 이름")
    file_url: Mapped[str | None] = mapped_column(Text, comment="배치 파일 URL")
    file_size: Mapped[int | None] = mapped_column(BigInteger,comment="배치 파일 크기")
    date_from: Mapped[datetime | None] = mapped_column(DateTime,comment="주문 시작 일자")
    date_to: Mapped[datetime | None] = mapped_column(DateTime,comment="주문 종료 일자")
    error_message: Mapped[str | None] = mapped_column(Text,comment="배치 프로세스 오류 메시지")
    created_by: Mapped[str | None] = mapped_column(String(100),comment="배치 프로세스 생성자 ID")
    work_status: Mapped[str | None] = mapped_column(String(14),comment="작업 상태")
    # 아래는 DB에 없는 필드
    # target_table: Mapped[str | None] = mapped_column(String(255),comment="처리 대상 테이블명")
    # target_table_ids: Mapped[list[int] | None] = mapped_column(ARRAY(BigInteger),comment="처리 대상 테이블 레코드 ID 배열")
    # batch_name: Mapped[str | None] = mapped_column(String(255),comment="배치 프로세스 이름")
    # file_hash: Mapped[str | None] = mapped_column(String(64),comment="배치 파일 해시 (무결성 검증용)")
    # total_records: Mapped[int | None] = mapped_column(Integer,comment="처리 대상 레코드 수")
    # success_records: Mapped[int | None] = mapped_column(Integer,comment="성공 레코드 수")
    # fail_records: Mapped[int | None] = mapped_column(Integer,comment="실패 레코드 수")
    # skip_records: Mapped[int | None] = mapped_column(Integer,comment="건너뛴 레코드 수")
