from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


# ============= printWbls Request Schema =============

class AddressItem(BaseModel):
    """주소 목록 아이템"""
    csr_num: Optional[str] = Field(None, max_length=7, description="계약번호")
    address: Optional[str] = Field(None, max_length=4000, description="배송지 주소")
    snd_zip: Optional[str] = Field(None, max_length=10, description="출발지 우편번호")
    rcv_zip: Optional[str] = Field(None, max_length=10, description="배송지 우편번호")
    msg_key: Optional[str] = Field(None, max_length=100, description="메세지KEY")

class PrintWblsRequest(BaseModel):
    """운송장 출력 요청"""
    address_list: List[AddressItem] = Field(..., description="주소목록")

# ============= printWbls Response Schema =============

class AddressResult(BaseModel):
    """주소 결과 아이템"""
    msg_key: Optional[str] = Field(None, description="메세지KEY - 자료 매칭을 위한 고객사 고유키")
    result_code: Optional[str] = Field(None, description="결과코드")
    result_message: Optional[str] = Field(None, description="결과메세지")
    s_tml_nam: Optional[str] = Field(None, description="집하지 터미널명")
    s_tml_cod: Optional[str] = Field(None, description="집하지 터미널코드")
    zip_cod: Optional[str] = Field(None, description="정제된 우편번호")
    tml_nam: Optional[str] = Field(None, description="도착지 터미널명")
    tml_cod: Optional[str] = Field(None, description="도착지 터미널코드")
    cen_nam: Optional[str] = Field(None, description="도착지 집배점명")
    cen_cod: Optional[str] = Field(None, description="도착지 집배점코드")
    pd_tim: Optional[str] = Field(None, description="집배소요시간")
    dom_rgn: Optional[str] = Field(None, description="권역구분")
    hub_cod: Optional[str] = Field(None, description="허브코드")
    dom_mid: Optional[str] = Field(None, description="중분류코드")
    es_cod: Optional[str] = Field(None, description="배송사원분류코드")
    grp_rnk: Optional[str] = Field(None, description="소분류코드")
    es_nam: Optional[str] = Field(None, description="배송사원명")
    prt_add: Optional[str] = Field(None, description="주소 출력정보")
    wbl_num: Optional[str] = Field(None, description="운송장번호")

class PrintWblsResponse(BaseModel):
    """운송장 출력 응답"""
    total_cnt: Optional[int] = Field(None, description="전체 건수")
    error_cnt: Optional[int] = Field(None, description="오류 건수")
    address_list: Optional[List[AddressResult]] = Field(None, description="주소 목록")


# ============= down_form_orders에서 hanjin_printwbls 생성 응답 스키마 =============

class CreatedRecord(BaseModel):
    """생성된 레코드 정보"""
    id: Optional[int] = Field(None, description="레코드 ID")
    idx: Optional[str] = Field(None, description="주문번호")
    prt_add: Optional[str] = Field(None, description="배송지 주소")
    zip_cod: Optional[str] = Field(None, description="배송지 우편번호")
    snd_zip: Optional[str] = Field(None, max_length=10, description="출발지 우편번호")

class CreatePrintwblsFromDownFormOrdersResponse(BaseModel):
    """down_form_orders에서 hanjin_printwbls 생성 응답"""
    message: Optional[str] = Field(None, description="처리 결과 메시지")
    processed_count: Optional[int] = Field(None, description="처리된 건수")
    created_records: Optional[List[CreatedRecord]] = Field(None, description="생성된 레코드 목록")
    error: Optional[str] = Field(None, description="오류 메시지")


# ============= hanjin_printwbls API 처리 응답 스키마 =============

class UpdatedRecord(BaseModel):
    """업데이트된 레코드 정보"""
    id: Optional[int] = Field(None, description="레코드 ID")
    idx: Optional[str] = Field(None, description="주문번호")
    msg_key: Optional[str] = Field(None, description="메시지 키")
    result_code: Optional[str] = Field(None, description="결과 코드")
    wbl_num: Optional[str] = Field(None, description="운송장번호")

class ApiResponseInfo(BaseModel):
    """API 응답 정보"""
    total_cnt: Optional[int] = Field(None, description="전체 건수")
    error_cnt: Optional[int] = Field(None, description="오류 건수")

class ProcessPrintwblsWithApiResponse(BaseModel):
    """hanjin_printwbls API 처리 응답"""
    message: Optional[str] = Field(None, description="처리 결과 메시지")
    processed_count: Optional[int] = Field(None, description="처리된 건수")
    api_response: Optional[ApiResponseInfo] = Field(None, description="API 응답 정보")
    updated_records: Optional[List[UpdatedRecord]] = Field(None, description="업데이트된 레코드 목록")
    error: Optional[str] = Field(None, description="오류 메시지")
