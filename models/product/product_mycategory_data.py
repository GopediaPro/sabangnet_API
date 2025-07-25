from __future__ import annotations
from decimal import Decimal
from typing import Optional
from sqlalchemy import BigInteger, String, Text, Numeric, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column
from models.base_model import Base


class ProductMycategoryData(Base):
    """
    상품 등록 원본 데이터 테이블 (product_mycategory_data) ORM 매핑
    """
    __tablename__ = "product_mycategory_data"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True, comment="고유 식별자"
    )
    # 기본 정보
    class_cd1: Mapped[str | None] = mapped_column(
        String(50), comment="대분류_분류코드"
    )
    class_nm1: Mapped[str | None] = mapped_column(
        String(50), comment="대분류_분류명"
    )
    class_pr1: Mapped[str | None] = mapped_column(
        String(50), comment="대분류_전시순서"
    )
    class_cd2: Mapped[str | None] = mapped_column(
        String(50), comment="중분류_분류코드"
    )
    class_nm2: Mapped[str | None] = mapped_column(
        String(50), comment="중분류_분류명"
    )
    class_pr2: Mapped[str | None] = mapped_column(
        String(50), comment="중분류_전시순서"
    )
    class_cd3: Mapped[str | None] = mapped_column(
        String(50), comment="소분류_분류코드"
    )
    class_nm3: Mapped[str | None] = mapped_column(
        String(50), comment="소분류_분류명"
    )
    class_pr3: Mapped[str | None] = mapped_column(
        String(50), comment="소분류_전시순서"
    )
    class_cd4: Mapped[str | None] = mapped_column(
        String(50), comment="세분류_분류코드"
    )
    class_nm4: Mapped[str | None] = mapped_column(
        String(50), comment="세분류_분류명"
    )
    class_pr4: Mapped[str | None] = mapped_column(
        String(50), comment="세분류_전시순서"
    )