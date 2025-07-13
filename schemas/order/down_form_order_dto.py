from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

# BaseDTO 정의 (없으면 추가)
class BaseDTO(BaseModel):
    def to_orm(self, orm_class):
        return orm_class(**self.model_dump())


class DownFormOrderDto(BaseDTO):
    """
    다운폼 주문 DTO (DB 스키마와 1:1 매핑)
    """
    # 기본 정보
    id: Optional[int] = Field(None, description="기본키")
    process_dt: Optional[datetime] = Field(None, description="처리 일시")
    form_name: Optional[str] = Field(None, max_length=30, description="폼 이름 (G마켓/옥션, 기본양식, 브랜디, 카카오 등)")
    seq: Optional[int] = Field(None, description="순번")
    idx: str = Field(..., max_length=50, description="사방넷주문번호")

    # 날짜 정보
    order_date: Optional[datetime] = Field(None, description="주문 일자")
    reg_date: Optional[str] = Field(None, max_length=14, description="수집일자 (형식: 년월일시분초 예: 20190305115959)")
    ord_confirm_date: Optional[str] = Field(None, max_length=14, description="주문 확인일자")
    rtn_dt: Optional[str] = Field(None, max_length=14, description="반품 완료일자")
    chng_dt: Optional[str] = Field(None, max_length=14, description="교환 완료일자")
    delivery_confirm_date: Optional[str] = Field(None, max_length=14, description="출고 완료일자")
    cancel_dt: Optional[str] = Field(None, max_length=14, description="취소 완료일자")
    hope_delv_date: Optional[str] = Field(None, max_length=14, description="배송희망일자")
    inv_send_dt: Optional[str] = Field(None, max_length=14, description="송장전송일자")

    # 주문 정보
    order_id: Optional[str] = Field(None, max_length=100, description="주문번호(쇼핑몰)")
    mall_order_id: Optional[str] = Field(None, description="부주문번호")

    # 상품 정보
    product_id: Optional[str] = Field(None, description="품번코드(사방넷)")
    product_name: Optional[str] = Field(None, description="상품명(수집)")
    mall_product_id: Optional[str] = Field(None, max_length=50, description="상품코드(쇼핑몰)")
    item_name: Optional[str] = Field(None, max_length=100, description="제품명")
    sku_value: Optional[str] = Field(None, description="옵션(수집)")
    sku_alias: Optional[str] = Field(None, description="옵션별칭")
    sku_no: Optional[str] = Field(None, description="SKU번호")
    barcode: Optional[str] = Field(None, description="바코드")
    model_name: Optional[str] = Field(None, description="모델명")
    erp_model_name: Optional[str] = Field(None, description="ERP업로드용_모델명")
    location_nm: Optional[str] = Field(None, description="Location")

    # 수량 및 가격 정보
    sale_cnt: Optional[int] = Field(None, description="수량")
    pay_cost: Optional[Decimal] = Field(None, description="결제금액")
    delv_cost: Optional[Decimal] = Field(None, description="배송비(수집)")
    total_cost: Optional[Decimal] = Field(None, description="주문금액")
    total_delv_cost: Optional[Decimal] = Field(None, description="주문금액/배송비(수집)")
    expected_payout: Optional[Decimal] = Field(None, description="정산예정금액")
    etc_cost: Optional[str] = Field(None, description="etc 금액 - 설명2")

    # 계산된 금액 정보
    price_formula: Optional[str] = Field(None, max_length=50, description="금액 계산 공식")
    service_fee: Optional[Decimal] = Field(None, description="서비스이용료")

    # 합포장용 합계 정보
    sum_p_ea: Optional[Decimal] = Field(None, description="EA(확정)(합포합계)")
    sum_expected_payout: Optional[Decimal] = Field(None, description="공급단가*수량(합포합계)")
    sum_pay_cost: Optional[Decimal] = Field(None, description="결제금액(합포합계)")
    sum_delv_cost: Optional[Decimal] = Field(None, description="배송비(합포합계)")
    sum_total_cost: Optional[Decimal] = Field(None, description="주문금액(합포합계)")

    # 수취인 정보
    receive_name: Optional[str] = Field(None, max_length=100, description="수취인명")
    receive_cel: Optional[str] = Field(None, max_length=20, description="수취인전화번호2")
    receive_tel: Optional[str] = Field(None, max_length=20, description="수취인전화번호1")
    receive_addr: Optional[str] = Field(None, description="수취인주소(4)")
    receive_zipcode: Optional[str] = Field(None, max_length=15, description="수취인우편번호(1)")

    # 배송 정보
    delivery_payment_type: Optional[str] = Field(None, max_length=10, description="배송결제(신용,착불)")
    delv_msg: Optional[str] = Field(None, description="배송메세지")
    delivery_id: Optional[str] = Field(None, description="택배사코드")
    delivery_class: Optional[str] = Field(None, description="운임비타입")
    invoice_no: Optional[str] = Field(None, description="송장번호")

    # 사이트 및 플랫폼 정보
    fld_dsp: Optional[str] = Field(None, description="사이트")

    # 기타 정보
    order_etc_6: Optional[str] = Field(None, description="자사몰필드6 - 서비스이용료")
    order_etc_7: Optional[str] = Field(None, description="자사몰필드7 - 판매자관리코드")
    etc_msg: Optional[str] = Field(None, description="기타메세지(카카오모델명)")
    free_gift: Optional[str] = Field(None, description="사은품")

    # 시스템 정보
    created_at: Optional[datetime] = Field(None, description="생성 일시")
    updated_at: Optional[datetime] = Field(None, description="수정 일시")

    model_config = ConfigDict(
        from_attributes=True
    )


class DownFormOrderRequest(BaseModel):
    template_code: str = Field(..., description="템플릿 코드")
    raw_data: List[Dict[str, Any]] = Field(..., description="원본 주문 데이터")

class DownFormOrderResponse(BaseModel):
    saved_count: int
    message: str

class DownFormOrderFilter(BaseModel):
    template_code: Optional[str]
    date_from: Optional[datetime]
    date_to: Optional[datetime]