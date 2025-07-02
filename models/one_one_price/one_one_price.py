"""
One One Price Data 모델
1+1 상품 가격 계산을 위한 데이터 테이블 매핑
"""

from __future__ import annotations
from decimal import Decimal
from typing import Optional
from sqlalchemy import BigInteger, Numeric, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from models.base_model import Base


class OneOnePrice(Base):
    """
    1+1 상품 가격 계산을 위한 데이터 테이블 (one_one_price) ORM 매핑
    """
    __tablename__ = "one_one_price"

    # 기본 정보
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        comment="고유 식별자")

    # 상품등록 FK
    product_registration_raw_data_id: Mapped[int] = mapped_column(
        ForeignKey(
            "product_registration_raw_data.id",
            name="product_registration_raw_data_id",
            ondelete="CASCADE"),
        nullable=False,
        comment="상품등록 FK")
    
    products_nm: Mapped[Optional[str]] = mapped_column(String(100), nullable=False)

    # 기준가격(전문몰 가격)
    standard_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 0), nullable=True, comment="기준가격")

    # 1+1가격, if(기준가 + 100 < 10000, roundup(기준가 * 2 + 2000, -3) - 100, roundup(기준가 * 2 + 1000, -3) - 100)
    one_one_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 0), nullable=True, comment="1+1가격")

    # roundup(1+1가격 * 1.15, -3) - 100
    shop0007: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 0), nullable=True, comment="GS Shop")
    shop0042: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 0), nullable=True, comment="텐바이텐")
    shop0087: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 0), nullable=True, comment="롯데홈쇼핑(신)")
    shop0094: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 0), nullable=True, comment="무신사")
    shop0121: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 0), nullable=True, comment="NS홈쇼핑(신)")
    shop0129: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 0), nullable=True, comment="CJ온스타일")
    shop0154: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 0), nullable=True, comment="K쇼핑")
    shop0650: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 0), nullable=True, comment="홈&쇼핑(신)")

    # roundup(1+1가격 * 1.05, -3) - 100
    shop0029: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 0), nullable=True, comment="YES24")
    shop0189: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 0), nullable=True, comment="오늘의집")
    shop0322: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 0), nullable=True, comment="브랜디")
    shop0444: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 0), nullable=True, comment="카카오스타일 (지그재그, 포스티)")
    shop0100: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 0), nullable=True, comment="신세계몰(신)")
    shop0298: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 0), nullable=True, comment="Cafe24(신) 유튜브쇼핑")
    shop0372: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 0), nullable=True, comment="롯데온")

    # 1+1가격 그대로 적용
    shop0381: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 0), nullable=True, comment="에이블리")
    shop0416: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 0), nullable=True, comment="아트박스(신)")
    shop0449: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 0), nullable=True, comment="카카오톡선물하기")
    shop0498: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 0), nullable=True, comment="올웨이즈")
    shop0583: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 0), nullable=True, comment="토스쇼핑")
    shop0587: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 0), nullable=True, comment="AliExpress")
    shop0661: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 0), nullable=True, comment="떠리몰")
    shop0075: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 0), nullable=True, comment="쿠팡")
    shop0319: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 0), nullable=True, comment="도매꾹")
    shop0365: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 0), nullable=True, comment="Grip")
    shop0387: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 0), nullable=True, comment="하프클럽(신)")

    # 1+1가격 + 100
    shop0055: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 0), nullable=True, comment="스마트스토어")
    shop0067: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 0), nullable=True, comment="ESM옥션")
    shop0068: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 0), nullable=True, comment="ESM지마켓")
    shop0273: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 0), nullable=True, comment="카카오톡스토어")
    shop0464: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 0), nullable=True, comment="11번가")

    def __repr__(self) -> str:
        return f"<OneOnePrice(id={self.id}), ProductRegistrationRawData(id={self.product_registration_raw_data_id})>"

    def to_dict(self) -> dict:
        """모델을 딕셔너리로 변환"""
        return {
            'id': self.id,
            'product_registration_raw_data_id': self.product_registration_raw_data_id,
            'products_nm': self.products_nm,
            'standard_price': self.standard_price,
            'one_one_price': self.one_one_price,
            'shop0007': self.shop0007,
            'shop0042': self.shop0042,
            'shop0087': self.shop0087,
            'shop0094': self.shop0094,
            'shop0121': self.shop0121,
            'shop0129': self.shop0129,
            'shop0154': self.shop0154,
            'shop0650': self.shop0650,
            'shop0029': self.shop0029,
            'shop0189': self.shop0189,
            'shop0322': self.shop0322,
            'shop0444': self.shop0444,
            'shop0100': self.shop0100,
            'shop0298': self.shop0298,
            'shop0372': self.shop0372,
            'shop0381': self.shop0381,
            'shop0416': self.shop0416,
            'shop0449': self.shop0449,
            'shop0498': self.shop0498,
            'shop0583': self.shop0583,
            'shop0587': self.shop0587,
            'shop0661': self.shop0661,
            'shop0075': self.shop0075,
            'shop0319': self.shop0319,
            'shop0365': self.shop0365,
            'shop0387': self.shop0387,
            'shop0055': self.shop0055,
            'shop0067': self.shop0067,
            'shop0068': self.shop0068,
            'shop0273': self.shop0273,
            'shop0464': self.shop0464,
        }
