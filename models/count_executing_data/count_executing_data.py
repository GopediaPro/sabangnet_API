from models.base_model import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, String, Integer, DateTime, func


class CountExecuting(Base):
    """
    상품 원본 데이터 테이블(count_executing)의 ORM 매핑 모델
    file 변환 중 실행중인 프로세스 카운트 저장
    """
    __tablename__ = "count_executing"

    # 기본 정보
    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True)
    count_nm: Mapped[str] = mapped_column(String(50))
    count_rev: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
