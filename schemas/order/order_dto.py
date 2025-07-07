from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field
from typing import List


class OrderDto(BaseModel):
    """
    주문 수집 데이터 전송 객체
    =============================================================================
    # 기본 정보
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    receive_dt: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=False))
    idx: Mapped[str | None] = mapped_column(String(50))
    order_id: Mapped[str | None] = mapped_column(String(100))
    mall_id: Mapped[str | None] = mapped_column(String(100))
    mall_user_id: Mapped[str | None] = mapped_column(String(100))
    mall_user_id2: Mapped[str | None] = mapped_column(String(100))
    order_status: Mapped[str | None] = mapped_column(String(50))

    # 주문자 정보
    user_id: Mapped[str | None] = mapped_column(String(100))
    user_name: Mapped[str | None] = mapped_column(String(100))
    user_tel: Mapped[str | None] = mapped_column(String(20))
    user_cel: Mapped[str | None] = mapped_column(String(20))
    user_email: Mapped[str | None] = mapped_column(String(200))

    # 수취인 정보
    receive_name: Mapped[str | None] = mapped_column(String(100))
    receive_tel: Mapped[str | None] = mapped_column(String(20))
    receive_cel: Mapped[str | None] = mapped_column(String(20))
    receive_email: Mapped[str | None] = mapped_column(String(200))
    receive_zipcode: Mapped[str | None] = mapped_column(String(10))
    receive_addr: Mapped[str | None] = mapped_column(Text)

    # 배송 및 메세지
    delv_msg: Mapped[str | None] = mapped_column(Text)
    delv_msg1: Mapped[str | None] = mapped_column(Text)
    mul_delv_msg: Mapped[str | None] = mapped_column(Text)
    etc_msg: Mapped[str | None] = mapped_column(Text)

    # 금액 정보
    total_cost: Mapped[Decimal | None] = mapped_column(Numeric(15, 2))
    pay_cost: Mapped[Decimal | None] = mapped_column(Numeric(15, 2))
    sale_cost: Mapped[Decimal | None] = mapped_column(Numeric(15, 2))
    mall_won_cost: Mapped[Decimal | None] = mapped_column(Numeric(15, 2))
    won_cost: Mapped[Decimal | None] = mapped_column(Numeric(15, 2))
    delv_cost: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))

    # 날짜 정보
    order_date: Mapped[datetime | None] = mapped_column(Date)
    reg_date: Mapped[str | None] = mapped_column(String(14))
    ord_confirm_date: Mapped[str | None] = mapped_column(String(14))
    rtn_dt: Mapped[str | None] = mapped_column(String(14))
    chng_dt: Mapped[str | None] = mapped_column(String(14))
    delivery_confirm_date: Mapped[str | None] = mapped_column(String(14))
    cancel_dt: Mapped[str | None] = mapped_column(String(14))
    hope_delv_date: Mapped[str | None] = mapped_column(String(14))
    inv_send_dm: Mapped[str | None] = mapped_column(String(14))

    # 업체 정보
    partner_id: Mapped[str | None] = mapped_column(String(100))
    dpartner_id: Mapped[str | None] = mapped_column(String(100))

    # 상품 정보
    mall_product_id: Mapped[str | None] = mapped_column(String(100))
    product_id: Mapped[str | None] = mapped_column(String(100))
    sku_id: Mapped[str | None] = mapped_column(String(100))
    p_product_name: Mapped[str | None] = mapped_column(Text)
    p_sku_value: Mapped[str | None] = mapped_column(Text)
    product_name: Mapped[str | None] = mapped_column(Text)
    sku_value: Mapped[str | None] = mapped_column(Text)
    compayny_goods_cd: Mapped[str | None] = mapped_column(String(255))
    sku_alias: Mapped[str | None] = mapped_column(String(200))
    goods_nm_pr: Mapped[str | None] = mapped_column(Text)
    goods_keyword: Mapped[str | None] = mapped_column(String(255))
    model_no: Mapped[str | None] = mapped_column(String(255))
    model_name: Mapped[str | None] = mapped_column(String(255))
    barcode: Mapped[str | None] = mapped_column(String(100))

    # 수량 및 구분 정보
    sale_cnt: Mapped[int | None] = mapped_column(Integer)
    box_ea: Mapped[int | None] = mapped_column(Integer)
    p_ea: Mapped[int | None] = mapped_column(Integer)
    delivery_method_str: Mapped[str | None] = mapped_column(String(100))
    delivery_method_str2: Mapped[str | None] = mapped_column(String(100))
    order_gubun: Mapped[str | None] = mapped_column(String(10))
    set_gubun: Mapped[str | None] = mapped_column(String(10))

    # 기타 처리 정보
    jung_chk_yn: Mapped[str | None] = mapped_column(String(2))
    mall_order_seq: Mapped[int | None] = mapped_column(BigInteger)
    mall_order_id: Mapped[str | None] = mapped_column(String(100))
    etc_field3: Mapped[str | None] = mapped_column(Text)
    ord_field2: Mapped[str | None] = mapped_column(String(10))
    copy_idx: Mapped[str | None] = mapped_column(String(50))

    # 분류 정보
    class_cd1: Mapped[str | None] = mapped_column(String(50))
    class_cd2: Mapped[str | None] = mapped_column(String(50))
    class_cd3: Mapped[str | None] = mapped_column(String(50))
    class_cd4: Mapped[str | None] = mapped_column(String(50))
    brand_nm: Mapped[str | None] = mapped_column(String(100))

    # 배송 정보
    delivery_id: Mapped[str | None] = mapped_column(String(50))
    invoice_no: Mapped[str | None] = mapped_column(String(100))
    inv_send_msg: Mapped[str | None] = mapped_column(Text)

    # 사은품 및 기타
    free_gift: Mapped[str | None] = mapped_column(Text)
    fld_dsp: Mapped[str | None] = mapped_column(Text)
    acnt_regs_srno: Mapped[int | None] = mapped_column(Integer)

    # 자사몰 확장 필드 (1~14)
    order_etc_1: Mapped[str | None] = mapped_column(Text)
    order_etc_2: Mapped[str | None] = mapped_column(Text)
    order_etc_3: Mapped[str | None] = mapped_column(Text)
    order_etc_4: Mapped[str | None] = mapped_column(Text)
    order_etc_5: Mapped[str | None] = mapped_column(Text)
    order_etc_6: Mapped[str | None] = mapped_column(Text)
    order_etc_7: Mapped[str | None] = mapped_column(Text)
    order_etc_8: Mapped[str | None] = mapped_column(Text)
    order_etc_9: Mapped[str | None] = mapped_column(Text)
    order_etc_10: Mapped[str | None] = mapped_column(Text)
    order_etc_11: Mapped[str | None] = mapped_column(Text)
    order_etc_12: Mapped[str | None] = mapped_column(Text)
    order_etc_13: Mapped[str | None] = mapped_column(Text)
    order_etc_14: Mapped[str | None] = mapped_column(Text)
    =============================================================================
    """

    # 기본 정보
    receive_dt: datetime = Field(..., description="수집 일시")
    idx: str = Field(..., description="인덱스")
    order_id: str = Field(..., description="주문 번호")
    mall_id: str = Field(..., description="몰 ID")
    mall_user_id: str = Field(..., description="몰 사용자 ID")
    mall_user_id2: str = Field(..., description="몰 사용자 ID2")
    order_status: str = Field(..., description="주문 상태")

    # 주문자 정보
    user_id: str = Field(..., description="사용자 ID")
    user_name: str = Field(..., description="사용자 이름")
    user_tel: str = Field(..., description="사용자 전화번호")
    user_cel: str = Field(..., description="사용자 휴대전화번호")
    user_email: str = Field(..., description="사용자 이메일")

    # 수취인 정보
    receive_name: str = Field(..., description="수취인 이름")
    receive_tel: str = Field(..., description="수취인 전화번호")
    receive_cel: str = Field(..., description="수취인 휴대전화번호")
    receive_email: str = Field(..., description="수취인 이메일")
    receive_zipcode: str = Field(..., description="수취인 우편번호")
    receive_addr: str = Field(..., description="수취인 주소")

    # 배송 및 메세지
    delv_msg: str = Field(..., description="배송 메시지")
    delv_msg1: str = Field(..., description="배송 메시지1")
    mul_delv_msg: str = Field(..., description="배송 메시지2")
    etc_msg: str = Field(..., description="기타 메시지")

    # 금액 정보
    total_cost: Decimal = Field(..., description="총 금액")
    pay_cost: Decimal = Field(..., description="결제 금액")
    sale_cost: Decimal = Field(..., description="판매 금액")
    mall_won_cost: Decimal = Field(..., description="몰 원 금액")
    won_cost: Decimal = Field(..., description="원 금액")
    delv_cost: Decimal = Field(..., description="배송 비용")

    # 날짜 정보
    order_date: datetime = Field(..., description="주문 날짜")
    reg_date: str = Field(..., description="등록 날짜")
    ord_confirm_date: str = Field(..., description="주문 확인 날짜")
    rtn_dt: str = Field(..., description="반품 날짜")
    chng_dt: str = Field(..., description="변경 날짜")
    delivery_confirm_date: str = Field(..., description="배송 확인 날짜")
    cancel_dt: str = Field(..., description="취소 날짜")
    hope_delv_date: str = Field(..., description="배송 예정 날짜")
    inv_send_dm: str = Field(..., description="배송 메시지")

    # 업체 정보
    partner_id: str = Field(..., description="업체 ID")
    dpartner_id: str = Field(..., description="업체 ID2")

    # 상품 정보
    mall_product_id: str = Field(..., description="몰 상품 ID")
    product_id: str = Field(..., description="상품 ID")
    sku_id: str = Field(..., description="SKU ID")
    p_product_name: str = Field(..., description="상품 이름")
    p_sku_value: str = Field(..., description="SKU 값")
    product_name: str = Field(..., description="상품 이름")
    sku_value: str = Field(..., description="SKU 값")
    compayny_goods_cd: str = Field(..., description="자사 상품 코드")
    sku_alias: str = Field(..., description="SKU 별칭")
    goods_nm_pr: str = Field(..., description="상품 이름")
    goods_keyword: str = Field(..., description="상품 키워드")
    model_no: str = Field(..., description="모델 번호")
    model_name: str = Field(..., description="모델 이름")
    barcode: str = Field(..., description="바코드")

    # 수량 및 구분 정보
    sale_cnt: int = Field(..., description="판매 수량")
    box_ea: int = Field(..., description="박스 수량")
    p_ea: int = Field(..., description="P 수량")
    delivery_method_str: str = Field(..., description="배송 방법")
    delivery_method_str2: str = Field(..., description="배송 방법2")
    order_gubun: str = Field(..., description="주문 구분")
    set_gubun: str = Field(..., description="세트 구분")
    jung_chk_yn: str = Field(..., description="정산 체크 여부")
    mall_order_seq: int = Field(..., description="몰 주문 순번")
    mall_order_id: str = Field(..., description="몰 주문 번호")
    etc_field3: str = Field(..., description="기타 필드3")
    ord_field2: str = Field(..., description="주문 필드2")
    copy_idx: str = Field(..., description="복사 인덱스")

    # 분류 정보
    class_cd1: str = Field(..., description="분류 코드1")
    class_cd2: str = Field(..., description="분류 코드2")
    class_cd3: str = Field(..., description="분류 코드3")
    class_cd4: str = Field(..., description="분류 코드4")
    brand_nm: str = Field(..., description="브랜드 이름")

    # 배송 정보
    delivery_id: str = Field(..., description="배송 ID")
    invoice_no: str = Field(..., description="송장 번호")
    inv_send_msg: str = Field(..., description="송장 메시지")

    # 사은품 및 기타
    free_gift: str = Field(..., description="사은품")
    fld_dsp: str = Field(..., description="필드 디스플레이")
    acnt_regs_srno: int = Field(..., description="계정 등록 순번")

    # 자사몰 확장 필드 (1~14)
    order_etc_1: str = Field(..., description="주문 기타1")
    order_etc_2: str = Field(..., description="주문 기타2")
    order_etc_3: str = Field(..., description="주문 기타3")
    order_etc_4: str = Field(..., description="주문 기타4")
    order_etc_5: str = Field(..., description="주문 기타5")
    order_etc_6: str = Field(..., description="주문 기타6")
    order_etc_7: str = Field(..., description="주문 기타7")
    order_etc_8: str = Field(..., description="주문 기타8")
    order_etc_9: str = Field(..., description="주문 기타9")
    order_etc_10: str = Field(..., description="주문 기타10")
    order_etc_11: str = Field(..., description="주문 기타11")
    order_etc_12: str = Field(..., description="주문 기타12")
    order_etc_13: str = Field(..., description="주문 기타13")
    order_etc_14: str = Field(..., description="주문 기타14")


class OrderBulkDto(BaseModel):
    success_count: int = Field(..., description="성공 건수")
    error_count: int = Field(..., description="실패 건수")
    success_idx: List[str] = Field(..., description="성공 인덱스")
    errors: List[str] = Field(..., description="실패 에러")
    success_data: List[OrderDto] = Field(..., description="성공 데이터")