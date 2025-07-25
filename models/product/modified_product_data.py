from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Integer, Numeric, SmallInteger, String, Text, ForeignKey, 
    CHAR, BigInteger
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.product.product_raw_data import ProductRawData
from models.base_model import Base


class ModifiedProductData(Base):
    """
    상품 데이터 테이블 (product_row_data)모델과 연결
    """
    __tablename__ = "test_product_modified_data"

    # 기본 정보
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    
    goods_nm: Mapped[str] = mapped_column(String(255), nullable=False)
    goods_keyword: Mapped[str | None] = mapped_column(String(60))
    model_nm: Mapped[str | None] = mapped_column(String(60))
    model_no: Mapped[str | None] = mapped_column(String(60))
    brand_nm: Mapped[str | None] = mapped_column(String(50))
    compayny_goods_cd: Mapped[str] = mapped_column(String(100), nullable=False)
    goods_search: Mapped[str | None] = mapped_column(String(255))

    # 분류·구분 코드
    goods_gubun: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    class_cd1: Mapped[str] = mapped_column(String(100), nullable=False)
    class_cd2: Mapped[str] = mapped_column(String(100), nullable=False)
    class_cd3: Mapped[str] = mapped_column(String(100), nullable=False)
    class_cd4: Mapped[str | None] = mapped_column(String(100))

    # --- 구분 (마스터, 전문몰, 1+1)
    gubun: Mapped[str] = mapped_column(String(10))

    # 거래처
    partner_id: Mapped[str | None] = mapped_column(String(50))
    dpartner_id: Mapped[str | None] = mapped_column(String(50))

    # 제조·원산지
    maker: Mapped[str | None] = mapped_column(String(50))
    origin: Mapped[str] = mapped_column(String(100), nullable=False)
    make_year: Mapped[str | None] = mapped_column(CHAR(4))
    make_dm: Mapped[str | None] = mapped_column(CHAR(8))

    # 시즌·성별·상태
    goods_season: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    sex: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    status: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    # 배송·세금
    deliv_able_region: Mapped[int | None] = mapped_column(SmallInteger)
    tax_yn: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    delv_type: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    delv_cost: Mapped[Decimal | None] = mapped_column(Numeric(12, 0))

    # 반품·가격
    banpum_area: Mapped[int | None] = mapped_column(SmallInteger)
    goods_cost: Mapped[Decimal] = mapped_column(Numeric(12, 0), nullable=False)
    goods_price: Mapped[Decimal] = mapped_column(Numeric(12, 0), nullable=False)
    goods_consumer_price: Mapped[Decimal] = mapped_column(Numeric(12, 0), nullable=False)
    goods_cost2: Mapped[Decimal | None] = mapped_column(Numeric(12, 0))

    # 옵션
    char_1_nm: Mapped[str | None] = mapped_column(String(100))
    char_1_val: Mapped[str | None] = mapped_column(Text)
    char_2_nm: Mapped[str | None] = mapped_column(String(100))
    char_2_val: Mapped[str | None] = mapped_column(Text)

    # 이미지 (대표 + 1-24)
    img_path: Mapped[str] = mapped_column(Text, nullable=False)
    img_path1: Mapped[str | None] = mapped_column(Text)
    img_path2: Mapped[str | None] = mapped_column(Text)
    img_path3: Mapped[str | None] = mapped_column(Text)
    img_path4: Mapped[str | None] = mapped_column(Text)
    img_path5: Mapped[str | None] = mapped_column(Text)
    img_path6: Mapped[str | None] = mapped_column(Text)
    img_path7: Mapped[str | None] = mapped_column(Text)
    img_path8: Mapped[str | None] = mapped_column(Text)
    img_path9: Mapped[str | None] = mapped_column(Text)
    img_path10: Mapped[str | None] = mapped_column(Text)
    img_path11: Mapped[str | None] = mapped_column(Text)
    img_path12: Mapped[str | None] = mapped_column(Text)
    img_path13: Mapped[str | None] = mapped_column(Text)
    img_path14: Mapped[str | None] = mapped_column(Text)
    img_path15: Mapped[str | None] = mapped_column(Text)
    img_path16: Mapped[str | None] = mapped_column(Text)
    img_path17: Mapped[str | None] = mapped_column(Text)
    img_path18: Mapped[str | None] = mapped_column(Text)
    img_path19: Mapped[str | None] = mapped_column(Text)
    img_path20: Mapped[str | None] = mapped_column(Text)
    img_path21: Mapped[str | None] = mapped_column(Text)
    img_path22: Mapped[str | None] = mapped_column(Text)
    img_path23: Mapped[str | None] = mapped_column(Text)
    img_path24: Mapped[str | None] = mapped_column(Text)

    # 상세/인증
    goods_remarks: Mapped[str | None] = mapped_column(Text, nullable=False)
    certno: Mapped[str | None] = mapped_column(Text)
    avlst_dm: Mapped[str | None] = mapped_column(CHAR(8))
    avled_dm: Mapped[str | None] = mapped_column(CHAR(8))
    issuedate: Mapped[str | None] = mapped_column(CHAR(8))
    certdate: Mapped[str | None] = mapped_column(CHAR(8))
    cert_agency: Mapped[str | None] = mapped_column(Text)
    certfield: Mapped[str | None] = mapped_column(Text)

    # 식품·재고
    material: Mapped[str | None] = mapped_column(Text)
    stock_use_yn: Mapped[str | None] = mapped_column(CHAR(1))


    # 옵션·속성 제어
    opt_type: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=2)
    prop1_cd: Mapped[str | None] = mapped_column(CHAR(3))

    # 속성값 1-33
    prop_val1: Mapped[str | None] = mapped_column(String(25))
    prop_val2: Mapped[str | None] = mapped_column(String(25))
    prop_val3: Mapped[str | None] = mapped_column(String(25))
    prop_val4: Mapped[str | None] = mapped_column(String(25))
    prop_val5: Mapped[str | None] = mapped_column(String(25))
    prop_val6: Mapped[str | None] = mapped_column(String(25))
    prop_val7: Mapped[str | None] = mapped_column(String(25))
    prop_val8: Mapped[str | None] = mapped_column(String(25))
    prop_val9: Mapped[str | None] = mapped_column(String(25))
    prop_val10: Mapped[str | None] = mapped_column(String(25))
    prop_val11: Mapped[str | None] = mapped_column(String(25))
    prop_val12: Mapped[str | None] = mapped_column(String(25))
    prop_val13: Mapped[str | None] = mapped_column(String(25))
    prop_val14: Mapped[str | None] = mapped_column(String(25))
    prop_val15: Mapped[str | None] = mapped_column(String(25))
    prop_val16: Mapped[str | None] = mapped_column(String(25))
    prop_val17: Mapped[str | None] = mapped_column(String(25))
    prop_val18: Mapped[str | None] = mapped_column(String(25))
    prop_val19: Mapped[str | None] = mapped_column(String(25))
    prop_val20: Mapped[str | None] = mapped_column(String(25))
    prop_val21: Mapped[str | None] = mapped_column(String(25))
    prop_val22: Mapped[str | None] = mapped_column(String(25))
    prop_val23: Mapped[str | None] = mapped_column(String(25))
    prop_val24: Mapped[str | None] = mapped_column(String(25))
    prop_val25: Mapped[str | None] = mapped_column(String(25))
    prop_val26: Mapped[str | None] = mapped_column(String(25))
    prop_val27: Mapped[str | None] = mapped_column(String(25))
    prop_val28: Mapped[str | None] = mapped_column(String(25))
    prop_val29: Mapped[str | None] = mapped_column(String(25))
    prop_val30: Mapped[str | None] = mapped_column(String(25))
    prop_val31: Mapped[str | None] = mapped_column(String(25))
    prop_val32: Mapped[str | None] = mapped_column(String(25))
    prop_val33: Mapped[str | None] = mapped_column(String(25))

    # 기타
    pack_code_str: Mapped[str | None] = mapped_column(Text)
    goods_nm_en: Mapped[str | None] = mapped_column(String(255))
    goods_nm_pr: Mapped[str | None] = mapped_column(String(255))
    goods_remarks2: Mapped[str | None] = mapped_column(Text)
    goods_remarks3: Mapped[str | None] = mapped_column(Text)
    goods_remarks4: Mapped[str | None] = mapped_column(Text)
    importno: Mapped[str | None] = mapped_column(String(100))
    origin2: Mapped[str | None] = mapped_column(String(50))
    expire_dm: Mapped[str | None] = mapped_column(CHAR(8))
    supply_save_yn: Mapped[str | None] = mapped_column(CHAR(1))
    descrition: Mapped[str | None] = mapped_column(
        Text)  # 오타 그대로 유지 (description -> descrition)
    
    product_nm: Mapped[str | None] = mapped_column(String(60), nullable=True)
    no_product: Mapped[int | None] = mapped_column(Integer, nullable=True)
    detail_img_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    no_word: Mapped[int | None] = mapped_column(Integer, nullable=True)
    no_keyword: Mapped[int | None] = mapped_column(Integer, nullable=True)
    product_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # 수정버전
    test_product_raw_data_id: Mapped[int] = mapped_column(
        ForeignKey("test_product_raw_data.id",
                   name="test_product_raw_data", ondelete="CASCADE"),
        nullable=False
    )
    rev: Mapped[int | None] = mapped_column(SmallInteger)

    raw = relationship("ProductRawData",
                       back_populates="modified_entries",
                       lazy="joined",
                       )
