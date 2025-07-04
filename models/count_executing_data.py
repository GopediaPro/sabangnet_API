from sqlalchemy import (
    BigInteger, SmallInteger, String, Text, Numeric, CHAR, Integer
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base_model import Base


class CountExecuting(Base):
    """
    상품 원본 데이터 테이블(count_executing)의 ORM 매핑 모델
    file 변환 중 실행중인 프로세스 카운트 저장
    """
    __tablename__ = "count_executing"

    # 기본 정보
    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True)
    product_create_db: Mapped[int] = mapped_column(Integer)
    
