"""
이카운트 매핑 관련 스키마
"""
import re
from pydantic import BaseModel, Field, model_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from core.settings import SETTINGS


class EcountBatchProcessRequest(BaseModel):
    """이카운트 배치 처리 요청 스키마"""
    order_from: Optional[str] = Field(None, description="주문일자 시작 (YYYYMMDD)")
    order_to: Optional[str] = Field(None, description="주문일자 종료 (YYYYMMDD)")
    template_code: str = Field(..., description="템플릿 코드")
    is_test: bool = Field(True, description="테스트 환경 여부")
    page_size: int = Field(100, description="페이지 크기")
    
    class Config:
        json_schema_extra = {
            "example": {
                "order_from": "20241201",
                "order_to": "20241225",
                "template_code": "DEFAULT_TEMPLATE",
                "is_test": True,
                "page_size": 100
            }
        }


class EcountSaleDto(BaseModel):
    """이카운트 판매 DTO"""
    com_code: Optional[str] = Field(None, description="회사코드")
    user_id: Optional[str] = Field(None, description="사용자ID")
    
    # 매핑된 판매 데이터
    upload_ser_no: Optional[int] = Field(None, description="순번")
    io_date: Optional[str] = Field(None, description="판매일자")
    cust: Optional[str] = Field(None, description="거래처코드")
    cust_des: Optional[str] = Field(None, description="거래처명")
    emp_cd: Optional[str] = Field(None, description="담당자")
    wh_cd: Optional[str] = Field(None, description="출하창고")
    io_type: Optional[str] = Field(None, description="구분(거래유형)")
    exchange_type: Optional[str] = Field(None, description="외화종류")
    u_memo1: Optional[str] = Field(None, description="E-MAIL")
    u_memo2: Optional[str] = Field(None, description="FAX")
    u_memo3: Optional[str] = Field(None, description="연락처")
    u_txt1: Optional[str] = Field(None, description="주소")
    
    # 품목 정보
    prod_cd: Optional[str] = Field(None, description="품목코드")
    prod_des: Optional[str] = Field(None, description="품목명")
    size_des: Optional[str] = Field(None, description="규격(주문번호)")
    qty: Optional[float] = Field(None, description="수량")
    price: Optional[float] = Field(None, description="단가")
    supply_amt: Optional[float] = Field(None, description="공급가액")
    vat_amt: Optional[float] = Field(None, description="부가세")
    remarks: Optional[str] = Field(None, description="고객정보")
    
    # 적요 필드들
    p_remarks1: Optional[str] = Field(None, description="송장번호")
    p_remarks2: Optional[str] = Field(None, description="배송메시지")
    p_remarks3: Optional[str] = Field(None, description="상품번호")
    
    # 금액 필드들
    p_amt1: Optional[float] = Field(None, description="정산예정금액")
    p_amt2: Optional[float] = Field(None, description="서비스이용료")
    
    # 기타 필드들
    item_des: Optional[str] = Field(None, description="운임비타입")
    temp_column_id1: Optional[str] = Field(None, description="SKU번호")
    
    # 메타 정보
    is_success: bool = Field(False, description="성공여부")
    slip_no: Optional[str] = Field(None, description="판매번호(ERP)")
    trace_id: Optional[str] = Field(None, description="로그확인용 일련번호")
    error_message: Optional[str] = Field(None, description="오류메시지")
    is_test: bool = Field(True, description="테스트 여부")
    
    @model_validator(mode='before')
    @classmethod
    def set_default_auth_info(cls, values):
        """환경변수에서 기본 인증 정보를 설정합니다."""
        if isinstance(values, dict):
            # com_code가 설정되지 않은 경우 환경변수에서 가져오기
            if not values.get('com_code'):
                values['com_code'] = SETTINGS.ECOUNT_COM_CODE
            if not values.get('user_id'):
                values['user_id'] = SETTINGS.ECOUNT_USER_ID
            
        
        return values
    
    def model_post_init(self, __context) -> None:
        """모델 초기화 후 검증을 수행합니다."""
        if not self.com_code:
            raise ValueError("com_code는 필수입니다. 환경변수 ECOUNT_COM_CODE 설정하세요.")
        if not self.user_id:
            raise ValueError("user_id는 필수입니다. 환경변수 ECOUNT_USER_ID 설정하세요.")

class EcountSaleItem(BaseModel):
    """이카운트 API SaleList 항목 스키마"""
    BulkDatas: dict  # 동적으로 생성되는 UPPER_SNAKE_CASE dict


class EcountApiRequest(BaseModel):
    """이카운트 API 실제 요청 형식"""
    SaleList: List[EcountSaleItem]

class EcountErrorDetail(BaseModel):
    """이카운트 API 오류 상세 정보"""
    ColCd: Optional[str] = Field(None, description="컬럼 코드")
    Message: Optional[str] = Field(None, description="오류 메시지")
    # 추가 필드들도 허용
    class Config:
        extra = "allow"

class EcountResultDetail(BaseModel):
    """이카운트 API 응답 결과 상세 정보"""
    IsSuccess: bool = Field(..., description="성공 여부")
    TotalError: str = Field(..., description="전체 오류 메시지")
    Errors: Optional[List[EcountErrorDetail]] = Field(None, description="오류 상세 정보")
    Code: Optional[str] = Field(None, description="코드")
    Line: Optional[int] = Field(None, description="라인 번호")
    # 추가 필드들도 허용
    class Config:
        extra = "allow"

class EcountApiResponseData(BaseModel):
    """이카운트 API 응답 데이터 스키마"""
    EXPIRE_DATE: str = Field(..., description="만료일자")
    QUANTITY_INFO: str = Field(..., description="시간당 연속 오류 제한 건수, 1시간 허용량, 1일 허용량")
    TRACE_ID: str = Field(..., description="추적 ID")
    SuccessCnt: int = Field(..., description="성공 건수")
    FailCnt: int = Field(..., description="실패 건수")
    ResultDetails: List[EcountResultDetail] = Field(..., description="결과 상세 정보")
    SlipNos: List[str] = Field(..., description="전표 번호 목록")
    
    # 추가 필드들도 허용
    class Config:
        extra = "allow"


class EcountApiResponse(BaseModel):
    """이카운트 API 응답 스키마"""
    Data: EcountApiResponseData = Field(..., description="응답 데이터")
    Status: str = Field(..., description="응답 상태 코드")
    Error: Optional[str] = Field(None, description="오류 메시지")
    Errors: Optional[str] = Field(None, description="오류들")
    Timestamp: str = Field(..., description="응답 시간")
    RequestKey: Optional[str] = Field(None, description="요청 키")
    IsEnableNoL4: bool = Field(..., description="L4 비활성화 여부")
    RefreshTimestamp: Optional[str] = Field(None, description="새로고침 타임스탬프")
    AsyncActionKey: Optional[str] = Field(None, description="비동기 액션 키")
    
    class Config:
        extra = "allow"
        json_schema_extra = {
            "example": {
                "Data": {
                    "EXPIRE_DATE": "",
                    "QUANTITY_INFO": "시간당 연속 오류 제한 건수 : 0/30, 1시간 허용량 : 9/6000, 1일 허용량 : 9/10000",
                    "TRACE_ID": "db6138411aad40e42dc5e209f65f6f3c",
                    "SuccessCnt": 2,
                    "FailCnt": 0,
                    "ResultDetails": [
                        {
                            "IsSuccess": True,
                            "TotalError": "[전표묶음0] OK",
                            "Errors": [],
                            "Code": None
                        }
                    ],
                    "SlipNos": ["20180612-2"]
                },
                "Status": "200",
                "Error": None,
                "Timestamp": "2018-06-12 13:23:11.262",
                "RequestKey": "",
                "IsEnableNoL4": False
            }
        }


class EcountBatchProcessResult(BaseModel):
    """이카운트 배치 처리 결과"""
    total_orders: int = Field(..., description="총 주문 수")
    processed_orders: int = Field(..., description="처리된 주문 수")
    success_count: int = Field(..., description="성공한 주문 수")
    fail_count: int = Field(..., description="실패한 주문 수")
    skipped_count: int = Field(..., description="건너뛴 주문 수 (이미 처리됨)")
    ecount_sales: List[EcountSaleDto] = Field(default=[], description="이카운트 판매 데이터")
    errors: List[str] = Field(default=[], description="오류 목록")
    processing_time: float = Field(..., description="처리 시간 (초)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_orders": 100,
                "processed_orders": 95,
                "success_count": 90,
                "fail_count": 5,
                "skipped_count": 5,
                "ecount_sales": [],
                "errors": ["일부 주문에서 필수 필드 누락"],
                "processing_time": 45.6
            }
        }


class EcountBatchProcessResponse(BaseModel):
    """이카운트 배치 처리 응답"""
    success: bool = Field(..., description="전체 성공 여부")
    message: str = Field(..., description="결과 메시지")
    result: EcountBatchProcessResult = Field(..., description="처리 결과")
    timestamp: datetime = Field(default_factory=datetime.now, description="처리 시간")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "배치 처리가 완료되었습니다.",
                "result": {
                    "total_orders": 100,
                    "processed_orders": 95,
                    "success_count": 90,
                    "fail_count": 5,
                    "skipped_count": 5,
                    "ecount_sales": [],
                    "errors": [],
                    "processing_time": 45.6
                },
                "timestamp": "2024-12-25T10:30:00"
            }
        }

class EcountSaleRequest(BaseModel):
    sales: List[EcountSaleDto]

    class Config:
        json_schema_extra = {
            "example": {
                "sales": [
                    {
                    "upload_ser_no": 0,
                    "io_date": "20250718",
                    "cust": "9999999",
                    "emp_cd": "okokmart_test",
                    "wh_cd": "32",
                    "prod_cd": "test_sample1",
                    "qty": 99,
                    "price": 999999,
                    "remarks": "test"
                    }
                ]
            }
        }

class EcountSaleResponse(BaseModel):
    success: bool = Field(..., description="성공 여부")
    message: str = Field(..., description="응답 메시지")
    data: Optional[List[EcountSaleDto]] = Field(None, description="성공한 판매 데이터")
    errors: Optional[List[str]] = Field(None, description="오류 메시지 리스트")
    api_response: Optional[EcountApiResponseData] = Field(None, description="이카운트 API 응답 데이터")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "배치 처리 완료: 5건 성공, 0건 실패",
                "data": [],
                "errors": [],
                "api_response": {
                    "EXPIRE_DATE": "",
                    "QUANTITY_INFO": "시간당 연속 오류 제한 건수 : 0/30, 1시간 허용량 : 9/6000, 1일 허용량 : 9/10000",
                    "TRACE_ID": "db6138411aad40e42dc5e209f65f6f3c",
                    "SuccessCnt": 5,
                    "FailCnt": 0,
                    "ResultDetails": [
                        {
                            "IsSuccess": True,
                            "TotalError": "[전표묶음0] OK",
                            "Errors": [],
                            "Code": None
                        }
                    ],
                    "SlipNos": ["20180612-1", "20180612-2"]
                }
            }
        }

# 범용 변환 함수

def snake_to_upper_snake(d: dict) -> dict:
    """dict의 모든 snake_case 키를 UPPER_SNAKE_CASE로 변환 (재귀 지원)"""
    def convert_key(k):
        return k.upper()
    result = {}
    for k, v in d.items():
        if isinstance(v, dict):
            v = snake_to_upper_snake(v)
        elif isinstance(v, list):
            v = [snake_to_upper_snake(i) if isinstance(i, dict) else i for i in v]
        result[convert_key(k)] = v
    return result

def upper_snake_to_snake(d: dict) -> dict:
    """dict의 모든 UPPER_SNAKE_CASE 키를 snake_case로 변환 (재귀 지원)"""
    def to_snake(s):
        return s.lower()
    result = {}
    for k, v in d.items():
        if isinstance(v, dict):
            v = upper_snake_to_snake(v)
        elif isinstance(v, list):
            v = [upper_snake_to_snake(i) if isinstance(i, dict) else i for i in v]
        result[to_snake(k)] = v
    return result

# Pydantic 모델 <-> API dict 변환

def to_api_dict(model: BaseModel) -> dict:
    return snake_to_upper_snake(model.model_dump(exclude_unset=True))

def from_api_dict(api_data: dict, model_cls) -> BaseModel:
    return model_cls(**upper_snake_to_snake(api_data))

# 이카운트 API 요청 변환 함수

def convert_ecount_api_request_to_dto(api_request: EcountApiRequest) -> List[EcountSaleDto]:
    """이카운트 API 요청을 EcountSaleDto 리스트로 변환합니다."""
    result = []
    
    for sale_item in api_request.SaleList:
        bulk_data = sale_item.BulkDatas
        
        # BulkDatas를 snake_case로 변환
        bulk_dict = bulk_data.model_dump(exclude_unset=True)
        snake_dict = upper_snake_to_snake(bulk_dict)
        
        # EcountSaleDto로 변환
        sale_dto = EcountSaleDto(**snake_dict)
        result.append(sale_dto)
    
    return result

def convert_dto_to_ecount_api_request(sale_dtos: List[EcountSaleDto]) -> EcountApiRequest:
    """EcountSaleDto 리스트를 이카운트 API 요청 형식으로 변환합니다."""
    sale_items = []
    
    for sale_dto in sale_dtos:
        # EcountSaleDto를 snake_case dict로 변환
        dto_dict = sale_dto.model_dump(exclude_unset=True)
        
        # snake_case를 UPPER_SNAKE_CASE로 변환
        upper_dict = snake_to_upper_snake(dto_dict)
        
        # BulkDatas를 dict로 직접 생성
        sale_item = EcountSaleItem(BulkDatas=upper_dict)
        sale_items.append(sale_item)
    
    return EcountApiRequest(SaleList=sale_items)
