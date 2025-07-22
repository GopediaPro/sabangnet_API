"""
이카운트 인증 관련 스키마
"""
from pydantic import BaseModel, Field
from typing import Optional


class ZoneRequest(BaseModel):
    """Zone API 요청 스키마"""
    COM_CODE: str = Field(..., max_length=6, description="이카운트 ERP 로그인할 때 사용하는 회사코드")

    class Config:
        json_schema_extra = {
            "example": {
                "COM_CODE": "80001"
            }
        }


class ZoneResponseData(BaseModel):
    """Zone API 응답 데이터"""
    EXPIRE_DATE: Optional[str] = Field(None, description="주어진 날짜의 이카운트 API 현재버전서비스가 종료됩니다")
    ZONE: str = Field(..., max_length=6, description="로그인API 호출시 사용될 Zone 정보")
    DOMAIN: str = Field(..., max_length=30, description="로그인API 호출시 사용될 도메인 정보")


class ErrorDetail(BaseModel):
    """에러 상세 정보"""
    Code: Optional[int] = Field(None, description="오류코드")
    Message: Optional[str] = Field(None, description="오류내용")
    MessageDetail: Optional[str] = Field(None, description="오류상세정보")


class ZoneResponse(BaseModel):
    """Zone API 응답 스키마"""
    Data: Optional[ZoneResponseData] = Field(None, description="응답 데이터")
    Status: str = Field(..., description="처리결과")
    Error: Optional[ErrorDetail] = Field(None, description="오류가 발생할 경우")
    Timestamp: Optional[str] = Field(None, description="타임스탬프")


class LoginRequest(BaseModel):
    """로그인 API 요청 스키마"""
    COM_CODE: str = Field(..., max_length=6, description="이카운트 ERP 로그인할 때 사용하는 회사코드")
    USER_ID: str = Field(..., max_length=30, description="API_CERT_KEY를 발급받은 이카운트 ID")
    API_CERT_KEY: str = Field(..., max_length=50, description="테스트인증키")
    LAN_TYPE: str = Field(default="ko-KR", max_length=50, description="언어설정")
    ZONE: str = Field(..., max_length=2, description="DOMAIN ZONE")

    class Config:
        json_schema_extra = {
            "example": {
                "COM_CODE": "80001",
                "USER_ID": "USER_ID",
                "API_CERT_KEY": "{API_CERT_KEY}",
                "LAN_TYPE": "ko-KR",
                "ZONE": "C"
            }
        }


class LoginResponseDataDetails(BaseModel):
    """로그인 응답 세부 데이터"""
    COM_CODE: Optional[str] = Field(None, max_length=6, description="회사코드")
    USER_ID: Optional[str] = Field(None, max_length=30, description="사용자ID")
    SESSION_ID: Optional[str] = Field(None, max_length=50, description="세션ID")


class LoginResponseData(BaseModel):
    """로그인 응답 데이터"""
    EXPIRE_DATE: Optional[str] = Field(None, description="API 서비스 종료일")
    NOTICE: Optional[str] = Field(None, description="이카운트 API 공지사항")
    Code: Optional[str] = Field(None, description="응답 코드")
    Datas: Optional[LoginResponseDataDetails] = Field(None, description="로그인 세부 정보")
    Message: Optional[str] = Field(None, description="메시지")
    RedirectUrl: Optional[str] = Field(None, description="리다이렉트 URL")


class LoginResponse(BaseModel):
    """로그인 API 응답 스키마"""
    Data: Optional[LoginResponseData] = Field(None, description="응답 데이터")
    Status: Optional[str] = Field(None, description="처리결과")
    Error: Optional[ErrorDetail] = Field(None, description="오류가 발생할 경우")
    Timestamp: Optional[str] = Field(None, description="타임스탬프")


class EcountAuthInfo(BaseModel):
    """이카운트 인증 정보"""
    com_code: str = Field(..., description="회사코드")
    user_id: str = Field(..., description="사용자ID")
    api_cert_key: str = Field(..., description="API 인증키")
    zone: str = Field(..., description="Zone 정보")
    domain: Optional[str] = Field(None, description="도메인 정보")
    session_id: Optional[str] = Field(None, description="세션ID")

    class Config:
        json_schema_extra = {
            "example": {
                "com_code": "80001",
                "user_id": "USER_ID",
                "api_cert_key": "API_CERT_KEY",
                "zone": "C",
                "domain": ".ecount.com",
                "session_id": "39313231367c256562253866253939256563253838253938:0HDD9DBtZt2e"
            }
        }
