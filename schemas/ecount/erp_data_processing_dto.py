"""
ERP Data Processing DTOs
VBA 매크로 로직을 기반으로 한 데이터 처리용 DTO
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime


class ProcessedOrderData(BaseModel):
    """처리된 주문 데이터 (VBA Step 1-14 공통 처리 후)"""
    
    # 기본 정보
    seq: Optional[int] = Field(None, description="순번")
    fld_dsp: Optional[str] = Field(None, description="사이트")
    receive_name: Optional[str] = Field(None, description="수취인명")
    etc_cost: Optional[Decimal] = Field(None, description="금액")
    order_id: Optional[str] = Field(None, description="주문번호")
    
    # 상품 정보 (VBA Step 9에서 수량 텍스트 제거됨)
    item_name_only_name: Optional[str] = Field(None, description="제품명 (수량텍스트 제거됨)")
    erp_product_name: Optional[str] = Field(None, description="ERP품목명")
    
    # 수량 정보 (VBA Step 3-7에서 계산됨)
    devided_cnt: Optional[int] = Field(None, description="나눈수량")
    real_cnt: Optional[int] = Field(None, description="실수량")
    
    # 가격 정보 (VBA Step 8에서 계산됨)
    price: Optional[Decimal] = Field(None, description="단가")
    supply_amt: Optional[Decimal] = Field(None, description="공급가액")
    vat_amt: Optional[Decimal] = Field(None, description="부가세")
    
    # 적요 (VBA Step 12에서 생성됨)
    remarks: Optional[str] = Field(None, description="적요")
    
    # 연락처 정보
    receive_cel: Optional[str] = Field(None, description="전화번호1")
    receive_tel: Optional[str] = Field(None, description="전화번호2")
    receive_addr: Optional[str] = Field(None, description="수취인주소")
    receive_zipcode: Optional[str] = Field(None, description="우편번호")
    
    # 배송 정보
    delivery_method_str: Optional[str] = Field(None, description="선/착불")
    mall_product_id: Optional[str] = Field(None, description="상품번호")
    mall_product_id_sku: Optional[str] = Field(None, description="상품번호_SKU")
    delv_msg: Optional[str] = Field(None, description="배송메세지")
    
    # 정산 정보
    expected_payout: Optional[Decimal] = Field(None, description="정산예정금액")
    service_fee: Optional[Decimal] = Field(None, description="서비스이용료")
    mall_order_id: Optional[str] = Field(None, description="장바구니번호")
    invoice_no: Optional[str] = Field(None, description="운송장번호")
    order_etc_7: Optional[str] = Field(None, description="판매자관리코드")
    sku_no: Optional[str] = Field(None, description="SKU번호")
    
    # VBA Step 11에서 추가되는 정보
    site_code: Optional[str] = Field(None, description="사이트코드")
    
    class Config:
        from_attributes = True


class OKMartProcessedData(ProcessedOrderData):
    """OKMart 방식 처리된 데이터 (VBA Step 15-16 추가)"""
    
    # VBA Step 15에서 추가
    warehouse: Optional[str] = Field(None, description="창고")
    
    # VBA Step 16에서 추가
    purchase_price: Optional[Decimal] = Field(None, description="구매단가")
    purchase_supply_amt: Optional[Decimal] = Field(None, description="구매공급가")
    purchase_vat_amt: Optional[Decimal] = Field(None, description="구매부가세")
    
    # VBA Step 17에서 추가
    site_okmart: Optional[str] = Field(None, description="사이트-오케이마트")
    site_iyes: Optional[str] = Field(None, description="사이트-아이예스")
    emp_cd: Optional[str] = Field(None, description="담당자")
    io_type: Optional[str] = Field(None, description="거래유형")
    
    # 타임스탬프
    created_at: Optional[datetime] = Field(None, description="생성일시")
    updated_at: Optional[datetime] = Field(None, description="수정일시")


class IYESProcessedData(ProcessedOrderData):
    """IYES 방식 처리된 데이터 (VBA Step 15-17 추가)"""
    
    # VBA Step 15에서 추가
    warehouse: Optional[str] = Field(None, description="창고")
    warehouse_adjustment: Optional[str] = Field(None, description="창고조정")
    
    # VBA Step 16에서 추가
    purchase_price: Optional[Decimal] = Field(None, description="구매단가")
    purchase_supply_amt: Optional[Decimal] = Field(None, description="구매공급가")
    purchase_vat_amt: Optional[Decimal] = Field(None, description="구매부가세")
    
    # VBA Step 17에서 추가
    site_okmart: Optional[str] = Field(None, description="사이트-오케이마트")
    site_iyes: Optional[str] = Field(None, description="사이트-아이예스")
    emp_cd: Optional[str] = Field(None, description="담당자")
    io_type: Optional[str] = Field(None, description="거래유형")
    
    # 타임스탬프
    created_at: Optional[datetime] = Field(None, description="생성일시")
    updated_at: Optional[datetime] = Field(None, description="수정일시")


class EcountSaleData(BaseModel):
    """EcountSale 테이블 저장용 데이터 (1_판매입력.txt 기준)"""
    
    # 기본 정보
    com_code: str = Field("000001", description="회사코드")
    user_id: str = Field("system", description="사용자ID")
    emp_cd: Optional[str] = Field(None, description="담당자")
    
    # 거래 정보
    io_date: Optional[str] = Field(None, description="판매일자 (YYYYMMDD)")
    upload_ser_no: Optional[int] = Field(None, description="순번")
    cust: Optional[str] = Field(None, description="거래처코드")
    cust_des: Optional[str] = Field(None, description="거래처명")
    wh_cd: Optional[int] = Field(None, description="출하창고")
    io_type: Optional[str] = Field(None, description="거래유형")
    exchange_type: Optional[str] = Field(None, description="통화")
    exchange_rate: Optional[Decimal] = Field(None, description="환율")
    
    # 연락처 정보
    u_memo1: Optional[str] = Field(None, description="E-MAIL")
    u_memo2: Optional[str] = Field(None, description="FAX")
    u_memo3: Optional[str] = Field(None, description="연락처")
    u_txt1: Optional[str] = Field(None, description="주소")
    u_memo4: Optional[str] = Field(None, description="매장판매 결제구분")
    u_memo5: Optional[str] = Field(None, description="매장판매 거래구분")
    
    # 상품 정보
    prod_cd: Optional[str] = Field(None, description="품목코드")
    prod_des: Optional[str] = Field(None, description="품목명")
    qty: Optional[Decimal] = Field(None, description="수량")
    price: Optional[Decimal] = Field(None, description="단가")
    # exchange_cost: Optional[Decimal] = Field(None, description="외화금액")
    supply_amt: Optional[Decimal] = Field(None, description="공급가액")
    vat_amt: Optional[Decimal] = Field(None, description="부가세")
    
    # 고객 정보
    remarks: Optional[str] = Field(None, description="고객정보")
    p_remarks2: Optional[str] = Field(None, description="배송메시지")
    p_remarks1: Optional[str] = Field(None, description="송장번호")
    p_remarks3: Optional[str] = Field(None, description="상품번호")
    size_des: Optional[str] = Field(None, description="주문번호")
    p_amt1: Optional[Decimal] = Field(None, description="정산예정금액")
    p_amt2: Optional[Decimal] = Field(None, description="서비스이용료")
    item_cd: Optional[str] = Field(None, description="운임비타입")
    
    # 메타 정보
    is_test: bool = Field(True, description="테스트 여부")
    work_status: str = Field("ERP 업로드 전", description="작업상태")
    batch_id: Optional[str] = Field(None, description="배치ID")
    template_code: Optional[str] = Field(None, description="템플릿코드")
    
    # 타임스탬프
    created_at: Optional[datetime] = Field(None, description="생성일시")
    updated_at: Optional[datetime] = Field(None, description="수정일시")


class EcountPurchaseData(BaseModel):
    """EcountPurchase 테이블 저장용 데이터 (구매입력.txt 기준)"""
    
    # 기본 정보
    com_code: str = Field("000001", description="회사코드")
    user_id: str = Field("system", description="사용자ID")
    emp_cd: str = Field("system", description="담당자")
    
    # 거래 정보
    io_date: Optional[str] = Field(None, description="구매일자 (YYYYMMDD)")
    upload_ser_no: Optional[int] = Field(None, description="순번")
    cust: Optional[str] = Field(None, description="거래처코드")
    cust_des: Optional[str] = Field(None, description="거래처명")
    wh_cd: Optional[int] = Field(None, description="입고창고")
    io_type: str = Field("2", description="거래유형 (구매)")
    exchange_type: Optional[str] = Field("KRW", description="통화")
    exchange_rate: Optional[Decimal] = Field(1.0, description="환율")
    
    # 연락처 정보
    u_memo1: Optional[str] = Field(None, description="E-MAIL")
    u_memo2: Optional[str] = Field(None, description="FAX")
    u_memo3: Optional[str] = Field(None, description="연락처")
    u_txt1: Optional[str] = Field(None, description="주소")
    
    # 상품 정보
    prod_cd: Optional[str] = Field(None, description="품목코드")
    prod_des: Optional[str] = Field(None, description="품목명")
    qty: Optional[Decimal] = Field(None, description="수량")
    price: Optional[Decimal] = Field(None, description="단가")
    # exchange_cost: Optional[Decimal] = Field(None, description="외화금액")
    supply_amt: Optional[Decimal] = Field(None, description="공급가액")
    vat_amt: Optional[Decimal] = Field(None, description="부가세")
    
    # 기타 정보
    remarks: Optional[str] = Field(None, description="적요")
    
    # 메타 정보
    is_test: bool = Field(True, description="테스트 여부")
    work_status: str = Field("ERP 업로드 전", description="작업상태")
    batch_id: Optional[str] = Field(None, description="배치ID")
    template_code: Optional[str] = Field(None, description="템플릿코드")


class ERPProcessingResult(BaseModel):
    """ERP 처리 결과"""
    
    excel_data: Dict[str, List[Dict[str, Any]]] = Field(..., description="Excel용 데이터 (main_data, ecount_data)")
    ecount_erp_data: List = Field(..., description="EcountSale/Purchase 저장용 데이터")
    batch_id: str = Field(..., description="배치 ID")
    form_name: str = Field(..., description="처리된 Form Name")
    total_records: int = Field(..., description="총 레코드 수")
    processed_records: int = Field(..., description="처리된 레코드 수")
