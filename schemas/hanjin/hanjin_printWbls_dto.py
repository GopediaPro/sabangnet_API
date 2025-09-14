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

class CreateAndProcessPrintwblsRequest(BaseModel):
    """down_form_orders에서 printwbls 생성 및 처리 요청"""
    limit: Optional[int] = Field(100, description="처리할 최대 건수 (기본값: 100)")
    order_date_from: Optional[str] = Field(None, description="주문 시작 날짜 (YYYY-MM-DD)")
    order_date_to: Optional[str] = Field(None, description="주문 종료 날짜 (YYYY-MM-DD)")

class ProcessDetail(BaseModel):
    """처리 상세 정보"""
    idx: str = Field(..., description="주문번호")
    success: bool = Field(..., description="처리 성공 여부")
    invoice_no: Optional[str] = Field(None, description="운송장번호")
    error_message: Optional[str] = Field(None, description="에러 메시지")

class CreateAndProcessPrintwblsResponse(BaseModel):
    """down_form_orders에서 printwbls 생성 및 처리 응답"""
    total_processed: int = Field(..., description="총 처리 건수")
    success_count: int = Field(..., description="성공 건수")
    failed_count: int = Field(..., description="실패 건수")
    created_printwbls_count: int = Field(..., description="생성된 printwbls 건수")
    updated_down_form_orders_count: int = Field(..., description="업데이트된 down_form_orders 건수")
    details: List[ProcessDetail] = Field(..., description="처리 상세 정보")
    message: Optional[str] = Field(None, description="처리 결과 메시지")
    error: Optional[str] = Field(None, description="오류 메시지")
    batch_id: Optional[int] = Field(None, description="배치 프로세스 ID")


# ============= Excel 다운로드 관련 스키마 =============

class DownloadExcelFormRequest(BaseModel):
    """Excel 폼 다운로드 요청"""
    reg_date_from: str = Field(..., description="수집일자 시작 (YYYYMMDD)", example="20250611")
    reg_date_to: str = Field(..., description="수집일자 종료 (YYYYMMDD)", example="20250930")
    form_name: str = Field(default="generic_delivery", description="양식코드 (예: gmarket_bundle, basic_bundle, kakao_bundle, generic_delivery)", example="generic_delivery")

class DownloadExcelFormResponse(BaseModel):
    """Excel 폼 다운로드 응답"""
    batch_id: int = Field(..., description="배치 프로세스 ID")
    file_url: str = Field(..., description="파일 다운로드 URL")
    file_name: str = Field(..., description="파일명")
    file_size: int = Field(..., description="파일 크기 (bytes)")
    processed_count: int = Field(..., description="처리된 데이터 건수")
    message: Optional[str] = Field(None, description="처리 결과 메시지")


# ============= Excel 업로드 관련 스키마 =============

class UploadExcelFormRequest(BaseModel):
    """Excel 폼 업로드 요청"""
    pass  # 파일 업로드만 필요하므로 빈 스키마


class UpdatedRecord(BaseModel):
    """업데이트된 레코드 정보"""
    idx: str = Field(..., description="주문번호")
    invoice_no: str = Field(..., description="운송장번호")
    fld_dsp: Optional[str] = Field(None, description="도서")
    order_id: Optional[str] = Field(None, description="주문ID")
    form_name: Optional[str] = Field(None, description="양식코드")
    success: bool = Field(..., description="업데이트 성공 여부")
    error_message: Optional[str] = Field(None, description="에러 메시지")


class UploadExcelFormResponse(BaseModel):
    """Excel 폼 업로드 응답"""
    batch_id: int = Field(..., description="배치 프로세스 ID")
    file_url: str = Field(..., description="파일 다운로드 URL")
    file_name: str = Field(..., description="파일명")
    file_size: int = Field(..., description="파일 크기 (bytes)")
    total_processed: int = Field(..., description="총 처리 건수")
    success_count: int = Field(..., description="성공 건수")
    failed_count: int = Field(..., description="실패 건수")
    updated_data: List[UpdatedRecord] = Field(..., description="업데이트된 데이터 목록")
    message: str = Field(..., description="처리 결과 메시지")
