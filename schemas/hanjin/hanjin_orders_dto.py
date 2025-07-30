from pydantic import BaseModel, Field
from typing import List, Optional


# ============= insertOrder Request Schema =============

class CommodityItem(BaseModel):
    """상품 아이템"""
    commodity_cd: Optional[str] = Field(None, description="상품코드")
    commodity_nm: Optional[str] = Field(None, description="상품명")
    commodity_cnt: Optional[int] = Field(None, description="상품수량")

class InsertOrderRequest(BaseModel):
    """주문 등록 요청"""
    # 
    cust_edi_cd: Optional[str] = Field(None, description="EDI코드")
    cust_ord_no: Optional[str] = Field(None, description="주문번호")
    svc_cat_cd: Optional[str] = Field(None, regex="^[SFER]$", description="배송구분(S:출고, F:포커스, E:직택배, R:반품)")
    contract_no: Optional[str] = Field(None, description="계약번호")
    pickup_ask_dt: Optional[str] = Field(None, regex="^\\d{8}$", description="주문 전송일(YYYYMMDD)")
    
    # 송하인 정보
    sndr_zip: Optional[str] = Field(None, description="송하인 우편번호")
    sndr_base_addr: Optional[str] = Field(None, description="송하인 주소1")
    sndr_dtl_addr: Optional[str] = Field(None, description="송하인 주소2")
    sndr_nm: Optional[str] = Field(None, description="송하인명")
    sndr_tel_no: Optional[str] = Field(None, description="송하인 전화번호")
    
    # 수하인 정보 
    rcvr_zip: Optional[str] = Field(None, description="수하인 우편번호")
    rcvr_base_addr: Optional[str] = Field(None, description="수하인 주소1")
    rcvr_dtl_addr: Optional[str] = Field(None, description="수하인 주소2")
    rcvr_nm: Optional[str] = Field(None, description="수하인명")
    rcvr_tel_no: Optional[str] = Field(None, description="수하인 전화번호")
    
    # 상품 및 배송 정보
    commodity_nm: Optional[str] = Field(None, description="상품명")
    pay_typ_cd: Optional[str] = Field(None, regex="^(CD|CT|PP|CC)$", description="지불조건")
    box_typ_cd: Optional[str] = Field(None, regex="^[SABCDE]$", description="박스타입")
    
    # 선택 필드들
    wbl_no: Optional[str] = Field(None, description="운송장번호")
    sndr_mobile_no: Optional[str] = Field(None, description="송하인 핸드폰번호")
    sndr_ask_content: Optional[str] = Field(None, description="송하인 배송메시지")
    sndr_ref_content: Optional[str] = Field(None, description="송하인 담당자명")
    rcvr_mobile_no: Optional[str] = Field(None, description="수하인 핸드폰번호")
    rcvr_ask_content: Optional[str] = Field(None, description="수하인 배송메시지")
    rcvr_ref_content: Optional[str] = Field(None, description="수하인 담당자명")
    print_memo1: Optional[str] = Field(None, description="메모1")
    print_memo2: Optional[str] = Field(None, description="메모2")
    print_memo3: Optional[str] = Field(None, description="메모3")
    print_memo4: Optional[str] = Field(None, description="메모4")
    
    # 상품 리스트 (선택)
    commodity_list: Optional[List[CommodityItem]] = Field(None, description="상품리스트")

# ============= insertOrder Response Schema =============

class InsertOrderResponse(BaseModel):
    """주문 등록 응답"""
    result_code: Optional[str] = Field(None, description="결과코드")
    result_message: Optional[str] = Field(None, description="결과메세지")
    wbl_no: Optional[str] = Field(None, description="운송장번호")
    cust_ord_no: Optional[str] = Field(None, description="주문번호")
