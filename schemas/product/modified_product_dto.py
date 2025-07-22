from __future__ import annotations

from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class ModifiedProductDataDto(BaseModel):
    """test_product_modified_data DTO"""

    class Config:
        from_attributes = True

    # 기본 정보
    test_product_raw_data_id: int = Field(..., description="원본 상품 데이터 FK(BigInt)")
    rev: Optional[int] = Field(None, description="수정 차수")

    goods_nm: str = Field(..., max_length=255, description="상품명")
    goods_keyword: Optional[str] = Field(None, max_length=60, description="상품약어")
    model_nm: Optional[str] = Field(None, max_length=60, description="모델명")
    model_no: Optional[str] = Field(None, max_length=60, description="모델 No")
    brand_nm: Optional[str] = Field(None, max_length=50, description="브랜드명")
    compayny_goods_cd: str = Field(..., max_length=100, description="자체상품코드")
    goods_search: Optional[str] = Field(None, max_length=255, description="사이트검색어")

    # 분류·구분 코드
    goods_gubun: int = Field(..., ge=1, le=5, description="상품구분(1~5)")
    class_cd1: str = Field(..., max_length=100, description="대분류코드")
    class_cd2: str = Field(..., max_length=100, description="중분류코드")
    class_cd3: str = Field(..., max_length=100, description="소분류코드")
    class_cd4: Optional[str] = Field(None, max_length=100, description="세분류코드")
    gubun: Optional[str] = Field(None, max_length=10, description="몰구분")

    # 거래처
    partner_id: Optional[str] = Field(None, max_length=50, description="매입처 ID")
    dpartner_id: Optional[str] = Field(None, max_length=50, description="물류처 ID")

    # 제조·원산지
    maker: Optional[str] = Field(None, max_length=50, description="제조사")
    origin: str = Field(..., max_length=100, description="원산지(제조국)")
    make_year: Optional[str] = Field(None, min_length=4, max_length=4, description="생산연도")
    make_dm: Optional[str] = Field(None, min_length=8, max_length=8, description="제조일자(yyyymmdd)")

    # 시즌·성별·상태
    goods_season: int = Field(..., ge=1, le=7, description="시즌(1~7)")
    sex: int = Field(..., ge=1, le=4, description="남녀구분(1~4)")
    status: int = Field(..., ge=1, le=6, description="상품상태(1~6)")

    # 배송·세금
    deliv_able_region: Optional[int] = Field(None, ge=1, le=4, description="판매지역(1~4)")
    tax_yn: int = Field(..., ge=1, le=4, description="세금구분(1~4)")
    delv_type: int = Field(..., ge=1, le=4, description="배송비구분(1~4)")
    delv_cost: Optional[Decimal] = Field(None, ge=0, description="배송비")

    # 반품·가격
    banpum_area: Optional[int] = Field(None, description="반품지구분")
    goods_cost: Decimal = Field(..., ge=0, description="원가")
    goods_price: Decimal = Field(..., ge=0, description="판매가")
    goods_consumer_price: Decimal = Field(..., ge=0, description="TAG가(소비자가)")
    goods_cost2: Optional[Decimal] = Field(None, ge=0, description="원가2(참고용)")

    # 옵션
    char_1_nm: Optional[str] = Field(None, max_length=100, description="옵션제목(1)")
    char_1_val: Optional[str] = Field(None, description="옵션상세명칭(1)")
    char_2_nm: Optional[str] = Field(None, max_length=100, description="옵션제목(2)")
    char_2_val: Optional[str] = Field(None, description="옵션상세명칭(2)")

    # 이미지
    img_path: str = Field(..., description="대표이미지")
    img_path1: Optional[str] = Field(None)
    img_path2: Optional[str] = Field(None)
    img_path3: Optional[str] = Field(None)
    img_path4: Optional[str] = Field(None)
    img_path5: Optional[str] = Field(None)
    img_path6: Optional[str] = Field(None)
    img_path7: Optional[str] = Field(None)
    img_path8: Optional[str] = Field(None)
    img_path9: Optional[str] = Field(None)
    img_path10: Optional[str] = Field(None)
    img_path11: Optional[str] = Field(None)
    img_path12: Optional[str] = Field(None)
    img_path13: Optional[str] = Field(None)
    img_path14: Optional[str] = Field(None)
    img_path15: Optional[str] = Field(None)
    img_path16: Optional[str] = Field(None)
    img_path17: Optional[str] = Field(None)
    img_path18: Optional[str] = Field(None)
    img_path19: Optional[str] = Field(None)
    img_path20: Optional[str] = Field(None)
    img_path21: Optional[str] = Field(None)
    img_path22: Optional[str] = Field(None)
    img_path23: Optional[str] = Field(None, description="인증서 이미지")
    img_path24: Optional[str] = Field(None, description="수입증명 이미지")

    # 상세/인증
    goods_remarks: str = Field(..., description="상품상세설명")
    certno: Optional[str] = Field(None)
    avlst_dm: Optional[str] = Field(None, min_length=8, max_length=8)
    avled_dm: Optional[str] = Field(None, min_length=8, max_length=8)
    issuedate: Optional[str] = Field(None, min_length=8, max_length=8)
    certdate: Optional[str] = Field(None, min_length=8, max_length=8)
    cert_agency: Optional[str] = Field(None)
    certfield: Optional[str] = Field(None)

    # 식품·재고
    material: Optional[str] = Field(None)
    stock_use_yn: Optional[str] = Field(None, min_length=1, max_length=1)

    # 옵션·속성 제어
    opt_type: int = Field(default=2)
    prop1_cd: Optional[str] = Field(None, min_length=3, max_length=3)

    # 속성값 1-33
    prop_val1: Optional[str] = Field(None, max_length=25)
    prop_val2: Optional[str] = Field(None, max_length=25)
    prop_val3: Optional[str] = Field(None, max_length=25)
    prop_val4: Optional[str] = Field(None, max_length=25)
    prop_val5: Optional[str] = Field(None, max_length=25)
    prop_val6: Optional[str] = Field(None, max_length=25)
    prop_val7: Optional[str] = Field(None, max_length=25)
    prop_val8: Optional[str] = Field(None, max_length=25)
    prop_val9: Optional[str] = Field(None, max_length=25)
    prop_val10: Optional[str] = Field(None, max_length=25)
    prop_val11: Optional[str] = Field(None, max_length=25)
    prop_val12: Optional[str] = Field(None, max_length=25)
    prop_val13: Optional[str] = Field(None, max_length=25)
    prop_val14: Optional[str] = Field(None, max_length=25)
    prop_val15: Optional[str] = Field(None, max_length=25)
    prop_val16: Optional[str] = Field(None, max_length=25)
    prop_val17: Optional[str] = Field(None, max_length=25)
    prop_val18: Optional[str] = Field(None, max_length=25)
    prop_val19: Optional[str] = Field(None, max_length=25)
    prop_val20: Optional[str] = Field(None, max_length=25)
    prop_val21: Optional[str] = Field(None, max_length=25)
    prop_val22: Optional[str] = Field(None, max_length=25)
    prop_val23: Optional[str] = Field(None, max_length=25)
    prop_val24: Optional[str] = Field(None, max_length=25)
    prop_val25: Optional[str] = Field(None, max_length=25)
    prop_val26: Optional[str] = Field(None, max_length=25)
    prop_val27: Optional[str] = Field(None, max_length=25)
    prop_val28: Optional[str] = Field(None, max_length=25)
    prop_val29: Optional[str] = Field(None, max_length=25)
    prop_val30: Optional[str] = Field(None, max_length=25)
    prop_val31: Optional[str] = Field(None, max_length=25)
    prop_val32: Optional[str] = Field(None, max_length=25)
    prop_val33: Optional[str] = Field(None, max_length=25)

    # 기타
    pack_code_str: Optional[str] = Field(None)
    goods_nm_en: Optional[str] = Field(None, max_length=255)
    goods_nm_pr: Optional[str] = Field(None, max_length=255)
    goods_remarks2: Optional[str] = Field(None)
    goods_remarks3: Optional[str] = Field(None)
    goods_remarks4: Optional[str] = Field(None)
    importno: Optional[str] = Field(None, max_length=100)
    origin2: Optional[str] = Field(None, max_length=50)
    expire_dm: Optional[str] = Field(None, min_length=8, max_length=8)
    supply_save_yn: Optional[str] = Field(None, min_length=1, max_length=1)
    descrition: Optional[str] = Field(None)  # 오타 유지

    product_nm: Optional[str] = Field(None, max_length=60)
    no_product: Optional[int] = Field(None)
    detail_img_url: Optional[str] = Field(None)
    no_word: Optional[int] = Field(None)
    no_keyword: Optional[int] = Field(None)

    product_id: Optional[int] = Field(None, description="상품 ID")
