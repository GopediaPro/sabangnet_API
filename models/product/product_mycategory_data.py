from typing import Optional
from models.base_model import Base
from __future__ import annotations
from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column


class ProductMycategoryData(Base):
    """
    상품 등록 원본 데이터 테이블 (product_mycategory_data) ORM 매핑
    """
    __tablename__ = "product_mycategory_data"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True, comment="고유 식별자"
    )
    # 기본 정보
    class_cd1: Mapped[Optional[str]] = mapped_column(
        String(50), comment="대분류_분류코드", nullable=True
    )
    class_nm1: Mapped[Optional[str]] = mapped_column(
        String(50), comment="대분류_분류명", nullable=True
    )
    class_pr1: Mapped[Optional[str]] = mapped_column(
        String(50), comment="대분류_전시순서", nullable=True
    )
    class_cd2: Mapped[Optional[str]] = mapped_column(
        String(50), comment="중분류_분류코드", nullable=True
    )
    class_nm2: Mapped[Optional[str]] = mapped_column(
        String(50), comment="중분류_분류명", nullable=True
    )
    class_pr2: Mapped[Optional[str]] = mapped_column(
        String(50), comment="중분류_전시순서", nullable=True
    )
    class_cd3: Mapped[Optional[str]] = mapped_column(
        String(50), comment="소분류_분류코드", nullable=True
    )
    class_nm3: Mapped[Optional[str]] = mapped_column(
        String(50), comment="소분류_분류명", nullable=True
    )
    class_pr3: Mapped[Optional[str]] = mapped_column(
        String(50), comment="소분류_전시순서", nullable=True
    )
    class_cd4: Mapped[Optional[str]] = mapped_column(
        String(50), comment="세분류_분류코드", nullable=True
    )
    class_nm4: Mapped[Optional[str]] = mapped_column(
        String(50), comment="세분류_분류명", nullable=True
    )
    class_pr4: Mapped[Optional[str]] = mapped_column(
        String(50), comment="세분류_전시순서", nullable=True
    )