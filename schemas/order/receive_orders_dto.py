from decimal import Decimal
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ReceiveOrdersDto(BaseModel):
    """
    주문 수집 데이터 전송 객체
    """

    class Config:
        from_attributes = True

    # 기본 정보
    id: Optional[int] = Field(None, description="ID")
    receive_dt: Optional[datetime] = Field(None, description="수집 일시")
    idx: Optional[str] = Field(None, description="인덱스")
    order_id: Optional[str] = Field(None, description="주문 번호")
    mall_id: Optional[str] = Field(None, description="몰 ID")
    mall_user_id: Optional[str] = Field(None, description="몰 사용자 ID")
    mall_user_id2: Optional[str] = Field(None, description="몰 사용자 ID2")
    order_status: Optional[str] = Field(None, description="주문 상태")

    # 주문자 정보
    user_id: Optional[str] = Field(None, description="사용자 ID")
    user_name: Optional[str] = Field(None, description="사용자 이름")
    user_tel: Optional[str] = Field(None, description="사용자 전화번호")
    user_cel: Optional[str] = Field(None, description="사용자 휴대전화번호")
    user_email: Optional[str] = Field(None, description="사용자 이메일")

    # 수취인 정보
    receive_name: Optional[str] = Field(None, description="수취인 이름")
    receive_tel: Optional[str] = Field(None, description="수취인 전화번호")
    receive_cel: Optional[str] = Field(None, description="수취인 휴대전화번호")
    receive_email: Optional[str] = Field(None, description="수취인 이메일")
    receive_zipcode: Optional[str] = Field(None, description="수취인 우편번호")
    receive_addr: Optional[str] = Field(None, description="수취인 주소")

    # 배송 및 메세지
    delv_msg: Optional[str] = Field(None, description="배송 메시지")
    delv_msg1: Optional[str] = Field(None, description="배송 메시지1")
    mul_delv_msg: Optional[str] = Field(None, description="배송 메시지2")
    etc_msg: Optional[str] = Field(None, description="기타 메시지")

    # 금액 정보
    total_cost: Optional[Decimal] = Field(None, description="총 금액")
    pay_cost: Optional[Decimal] = Field(None, description="결제 금액")
    sale_cost: Optional[Decimal] = Field(None, description="판매 금액")
    mall_won_cost: Optional[Decimal] = Field(None, description="몰 원 금액")
    won_cost: Optional[Decimal] = Field(None, description="원 금액")
    delv_cost: Optional[Decimal] = Field(None, description="배송 비용")

    # 날짜 정보
    order_date: Optional[datetime] = Field(None, description="주문 날짜")
    reg_date: Optional[str] = Field(None, description="등록 날짜")
    ord_confirm_date: Optional[str] = Field(None, description="주문 확인 날짜")
    rtn_dt: Optional[str] = Field(None, description="반품 날짜")
    chng_dt: Optional[str] = Field(None, description="변경 날짜")
    delivery_confirm_date: Optional[str] = Field(None, description="배송 확인 날짜")
    cancel_dt: Optional[str] = Field(None, description="취소 날짜")
    hope_delv_date: Optional[str] = Field(None, description="배송 예정 날짜")
    inv_send_dm: Optional[str] = Field(None, description="배송 메시지")

    # 업체 정보
    partner_id: Optional[str] = Field(None, description="업체 ID")
    dpartner_id: Optional[str] = Field(None, description="업체 ID2")

    # 상품 정보
    mall_product_id: Optional[str] = Field(None, description="몰 상품 ID")
    product_id: Optional[str] = Field(None, description="상품 ID")
    sku_id: Optional[str] = Field(None, description="SKU ID")
    p_product_name: Optional[str] = Field(None, description="상품 이름")
    p_sku_value: Optional[str] = Field(None, description="SKU 값")
    product_name: Optional[str] = Field(None, description="상품 이름")
    sku_value: Optional[str] = Field(None, description="SKU 값")
    compayny_goods_cd: Optional[str] = Field(None, description="자사 상품 코드")
    sku_alias: Optional[str] = Field(None, description="SKU 별칭")
    goods_nm_pr: Optional[str] = Field(None, description="상품 이름")
    goods_keyword: Optional[str] = Field(None, description="상품 키워드")
    model_no: Optional[str] = Field(None, description="모델 번호")
    model_name: Optional[str] = Field(None, description="모델 이름")
    barcode: Optional[str] = Field(None, description="바코드")

    # 수량 및 구분 정보
    sale_cnt: Optional[int] = Field(None, description="판매 수량")
    box_ea: Optional[int] = Field(None, description="박스 수량")
    p_ea: Optional[int] = Field(None, description="P 수량")
    delivery_method_str: Optional[str] = Field(None, description="배송 방법")
    delivery_method_str2: Optional[str] = Field(None, description="배송 방법2")
    order_gubun: Optional[str] = Field(None, description="주문 구분")
    set_gubun: Optional[str] = Field(None, description="세트 구분")
    jung_chk_yn: Optional[str] = Field(None, description="정산 체크 여부")
    mall_order_seq: Optional[str] = Field(None, description="몰 주문 순번")
    mall_order_id: Optional[str] = Field(None, description="몰 주문 번호")
    etc_field3: Optional[str] = Field(None, description="기타 필드3")
    ord_field2: Optional[str] = Field(None, description="주문 필드2")
    copy_idx: Optional[str] = Field(None, description="복사 인덱스")

    # 분류 정보
    class_cd1: Optional[str] = Field(None, description="분류 코드1")
    class_cd2: Optional[str] = Field(None, description="분류 코드2")
    class_cd3: Optional[str] = Field(None, description="분류 코드3")
    class_cd4: Optional[str] = Field(None, description="분류 코드4")
    brand_nm: Optional[str] = Field(None, description="브랜드 이름")

    # 배송 정보
    delivery_id: Optional[str] = Field(None, description="배송 ID")
    invoice_no: Optional[str] = Field(None, description="송장 번호")
    inv_send_msg: Optional[str] = Field(None, description="송장 메시지")

    # 사은품 및 기타
    free_gift: Optional[str] = Field(None, description="사은품")
    fld_dsp: Optional[str] = Field(None, description="필드 디스플레이")
    acnt_regs_srno: Optional[int] = Field(None, description="계정 등록 순번")

    # 자사몰 확장 필드 (1~14)
    order_etc_1: Optional[str] = Field(None, description="주문 기타1")
    order_etc_2: Optional[str] = Field(None, description="주문 기타2")
    order_etc_3: Optional[str] = Field(None, description="주문 기타3")
    order_etc_4: Optional[str] = Field(None, description="주문 기타4")
    order_etc_5: Optional[str] = Field(None, description="주문 기타5")
    order_etc_6: Optional[str] = Field(None, description="주문 기타6")
    order_etc_7: Optional[str] = Field(None, description="주문 기타7")
    order_etc_8: Optional[str] = Field(None, description="주문 기타8")
    order_etc_9: Optional[str] = Field(None, description="주문 기타9")
    order_etc_10: Optional[str] = Field(None, description="주문 기타10")
    order_etc_11: Optional[str] = Field(None, description="주문 기타11")
    order_etc_12: Optional[str] = Field(None, description="주문 기타12")
    order_etc_13: Optional[str] = Field(None, description="주문 기타13")
    order_etc_14: Optional[str] = Field(None, description="주문 기타14")


class ReceiveOrdersBulkDto(BaseModel):
    """
    주문 수집 데이터 대량 전송 객체
    """

    class Config:
        from_attributes = True

    success_count: Optional[int] = Field(None, description="성공 건수")
    error_count: Optional[int] = Field(None, description="실패 건수")
    success_idx: Optional[list[str]] = Field(None, description="성공 인덱스")
    errors: Optional[list[str]] = Field(None, description="실패 에러")
    success_data: Optional[list[ReceiveOrdersDto]] = Field(None, description="성공 데이터")
