from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class DownFormOrderDto(BaseModel):
    """다운폼 주문 DTO"""

    id: int = Field(..., description="기본키")
    process_dt: Optional[datetime] = Field(None, description="처리 일시")
    form_name: Optional[str] = Field(None, max_length=30, description="출력서식명을 입력")
    seq: Optional[int] = Field(None, description="순번")
    fld_dsp: Optional[str] = Field(None, description="사이트")
    receive_name: Optional[str] = Field(None, max_length=100, description="수취인명")
    price_formula: Optional[str] = Field(None, max_length=50, description="금액(수식영역)")
    order_id: Optional[str] = Field(None, max_length=100, description="주문번호")
    item_name: Optional[str] = Field(None, max_length=100, description='제품명(SKU_ALIAS + " " + SALE_CNT + "개")')
    sale_cnt: Optional[int] = Field(None, description="수량")
    receive_cel: Optional[str] = Field(None, max_length=20, description="전화번호1")
    receive_tel: Optional[str] = Field(None, max_length=20, description="전화번호2")
    receive_addr: Optional[str] = Field(None, description="수취인주소")
    receive_zipcode: Optional[str] = Field(None, max_length=10, description="우편번호")
    delivery_payment_type: Optional[str] = Field(None, max_length=2, description="선/착불(CONVERT_NAME(DELIVERY_METHOD_STR))")
    mall_product_id: Optional[str] = Field(None, max_length=50, description="상품번호")
    delv_msg: Optional[str] = Field(None, description="배송메시지")
    expected_payout: Optional[Decimal] = Field(None, description="정산예정금액(MALL_WON_COST * SALE_CNT)")
    order_etc_6: Optional[Decimal] = Field(None, description="서비스이용료")
    mall_order_id: Optional[str] = Field(None, description="장바구니번호")
    delivery_no: Optional[str] = Field(None, description="운송장번호(빈칸)")
    delivery_class: Optional[str] = Field(None, description="운임비타입(Location)")
    seller_code: Optional[str] = Field(None, description="판매자관리코드(빈칸)")
    pay_cost: Optional[Decimal] = Field(None, description="금액[배송비미포함]")
    delv_cost: Optional[Decimal] = Field(None, description="배송비")
    product_id: Optional[str] = Field(None, description="사방넷품번코드")
    idx: str = Field(..., description="사방넷주문번호")
    product_name: Optional[str] = Field(None, description="수집상품명")
    sku_value: Optional[str] = Field(None, description="수집옵션")
    erp_model_name: Optional[str] = Field(None, description='ERP업로드용_모델명(BARCODE + " " + SALE_CNT + "개")')
    free_gift: Optional[str] = Field(None, description="사은품")
    pay_cost_minus_mall_won_cost_times_sale_cnt: Optional[Decimal] = Field(None, description="서비스이용료(PAY_COST - MALL_WON_COST * SALE_CNT)")
    total_cost: Optional[Decimal] = Field(None, description="금액")
    total_delv_cost: Optional[str] = Field(None, description="금액(TOTAL_COST & "/" & DELV_COST)")
    service_fee: Optional[str] = Field(None, description="서비스이용료(PAY_COST - MALL_WON_COST * SALE_CNT)")
    etc_msg: Optional[str] = Field(None, description="카카오모델명")
    sum_p_ea: Optional[str] = Field(None, description="수량(SUM(P_EA))")
    sum_expected_payout: Optional[Decimal] = Field(None, description="정산예정금액(SUM(MALL_WON_COST * SALE_CNT))")
    location_nm: Optional[str] = Field(None, description="Location")
    order_etc_7: Optional[str] = Field(None, description="금액[배송비미포함], 결재금액(SUM(PAY_COST))")
    sum_pay_cost: Optional[str] = Field(None, description="배송비(SUM(DELV_COST))")
    sum_delv_cost: Optional[str] = Field(None, description="배송비합계(SUM(DELV_COST))")
    sku_alias: Optional[str] = Field(None, description="옵션별칭")
    sum_total_cost: Optional[str] = Field(None, description="금액(SUM(TOTAL_COST))")
    model_name: Optional[str] = Field(None, description="모델명(Location+EA(상품)*수량개)")
    invoice_no: Optional[str] = Field(None, description="송장번호")
    sku_no: Optional[str] = Field(None, description='SKU번호(SKU_ALIAS + " " + SALE_CNT + "개")')
    barcode: Optional[str] = Field(None, description="적재위치")
    created_at: Optional[datetime] = Field(None, description="생성 일시")
    updated_at: Optional[datetime] = Field(None, description="수정 일시")

    model_config = ConfigDict(
        from_attributes=True
    )