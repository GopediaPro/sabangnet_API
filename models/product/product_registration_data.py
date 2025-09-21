"""
Product Registration Raw Data 모델
상품 등록 원본 데이터 테이블 매핑
"""

from __future__ import annotations
from decimal import Decimal
from typing import Optional
from sqlalchemy import BigInteger, String, Text, Numeric, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column
from models.base_model import Base


class ProductRegistrationRawData(Base):
    """
    상품 등록 원본 데이터 테이블 (product_registration_raw_data) ORM 매핑
    """
    __tablename__ = "product_registration_raw_data"

    # 기본 정보
    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True, comment="고유 식별자"
    )

    # 상품 기본 정보
    product_nm: Mapped[Optional[str]] = mapped_column(
        String(255), comment="제품명"
    )
    goods_nm: Mapped[Optional[str]] = mapped_column(
        String(255), comment="상품명"
    )
    detail_path_img: Mapped[Optional[str]] = mapped_column(
        Text, comment="상세페이지경로(이미지폴더)"
    )

    # 배송 및 가격 정보
    delv_cost: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 0), comment="배송비"
    )
    goods_search: Mapped[Optional[str]] = mapped_column(
        String(255), comment="키워드"
    )
    goods_price: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 0), comment="판매가(유료배송)"
    )
    stock_use_yn: Mapped[Optional[str]] = mapped_column(
        String(1), comment="재고관리사용여부"
    )

    # 인증 및 진행 옵션
    certno: Mapped[Optional[str]] = mapped_column(
        Text, comment="인증번호"
    )
    char_process: Mapped[Optional[str]] = mapped_column(
        String(255), comment="진행옵션 가져오기"
    )

    # 옵션 정보
    char_1_nm: Mapped[Optional[str]] = mapped_column(
        Text, comment="옵션명1"
    )
    char_1_val: Mapped[Optional[str]] = mapped_column(
        Text, comment="옵션상세1"
    )
    char_2_nm: Mapped[Optional[str]] = mapped_column(
        Text, comment="옵션명2"
    )
    char_2_val: Mapped[Optional[str]] = mapped_column(
        Text, comment="옵션상세2"
    )
    char_1_val_one_plus: Mapped[Optional[str]] = mapped_column(
        Text, comment="1+1옵션(1단)"
    )
    char_2_val_one_plus: Mapped[Optional[str]] = mapped_column(
        Text, comment="1+1옵션(22단)"
    )
    # 이미지 정보
    img_path: Mapped[Optional[str]] = mapped_column(
        Text, comment="대표이미지"
    )
    img_path1: Mapped[Optional[str]] = mapped_column(
        Text, comment="종합몰(JPG)이미지"
    )
    img_path2: Mapped[Optional[str]] = mapped_column(
        Text, comment="부가이미지2"
    )
    img_path3: Mapped[Optional[str]] = mapped_column(
        Text, comment="부가이미지3"
    )
    img_path4: Mapped[Optional[str]] = mapped_column(
        Text, comment="부가이미지4"
    )
    img_path5: Mapped[Optional[str]] = mapped_column(
        Text, comment="부가이미지5"
    )

    # 상세 정보
    goods_remarks: Mapped[Optional[str]] = mapped_column(
        Text, comment="상세설명"
    )
    mobile_bn: Mapped[Optional[str]] = mapped_column(
        Text, comment="모바일배너"
    )
    one_plus_one_bn: Mapped[Optional[str]] = mapped_column(
        Text, comment="1+1배너"
    )
    goods_remarks_url: Mapped[Optional[str]] = mapped_column(
        Text, comment="상세설명url"
    )
    delv_one_plus_one: Mapped[Optional[str]] = mapped_column(
        String(100), comment="1+1옵션(배송)"
    )
    delv_one_plus_one_detail: Mapped[Optional[str]] = mapped_column(
        String(100), comment="1+1옵션상세"
    )

    # 카테고리 정보
    class_nm1: Mapped[Optional[str]] = mapped_column(
        String(50), comment="대분류_분류명"
    )
    class_nm2: Mapped[Optional[str]] = mapped_column(
        String(50), comment="중분류_분류명"
    )
    class_nm3: Mapped[Optional[str]] = mapped_column(
        String(50), comment="소분류_분류명"
    )
    class_nm4: Mapped[Optional[str]] = mapped_column(
        String(50), comment="세분류_분류명"
    )

    # def __repr__(self) -> str:
    #     return f"<ProductRegistrationRawData(id={self.id}, product_nm='{self.product_nm}', char_1_nm='{self.char_1_nm}')>"

    def to_dict(self) -> dict:
        """모델을 딕셔너리로 변환"""
        return {
            'id': self.id,
            'product_nm': self.product_nm,
            'goods_nm': self.goods_nm,
            'detail_path_img': self.detail_path_img,
            'delv_cost': float(self.delv_cost) if self.delv_cost else None,
            'goods_search': self.goods_search,
            'goods_price': float(self.goods_price) if self.goods_price else None,
            'stock_use_yn': self.stock_use_yn,
            'certno': self.certno,
            'char_process': self.char_process,
            'char_1_nm': self.char_1_nm,
            'char_1_val': self.char_1_val,
            'char_2_nm': self.char_2_nm,
            'char_2_val': self.char_2_val,
            'char_1_val_one_plus': self.char_1_val_one_plus,
            'char_2_val_one_plus': self.char_2_val_one_plus,
            'img_path': self.img_path,
            'img_path1': self.img_path1,
            'img_path2': self.img_path2,
            'img_path3': self.img_path3,
            'img_path4': self.img_path4,
            'img_path5': self.img_path5,
            'goods_remarks': self.goods_remarks,
            'mobile_bn': self.mobile_bn,
            'one_plus_one_bn': self.one_plus_one_bn,
            'goods_remarks_url': self.goods_remarks_url,
            'delv_one_plus_one': self.delv_one_plus_one,
            'delv_one_plus_one_detail': self.delv_one_plus_one_detail,
            'class_nm1': self.class_nm1,
            'class_nm2': self.class_nm2,
            'class_nm3': self.class_nm3,
            'class_nm4': self.class_nm4,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
