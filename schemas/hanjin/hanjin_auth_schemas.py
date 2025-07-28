"""
한진 API 인증 관련 스키마
"""
from pydantic import BaseModel, Field
from typing import Optional


class HmacRequest(BaseModel):
    """HMAC 인증 요청 스키마"""
    client_id: str = Field(..., description="한진발급 고객사(EDI) 코드")
    x_api_key: str = Field(..., description="API Secret Key")
    method: str = Field(default="GET", description="HTTP 메서드 (GET, POST, PUT, DELETE)")
    uri: str = Field(..., description="API URI (쿼리 파라미터 포함)")

    class Config:
        json_schema_extra = {
            "example": {
                "client_id": "HANJIN",
                "x_api_key": "your_secret_key_here",
                "method": "GET",
                "uri": "https://api-stg.hanjin.com/parcel-delivery/v1/tracking/tracking-wbl?test=123"
            }
        }


class HmacResponse(BaseModel):
    """HMAC 인증 응답 스키마"""
    Authorization: str = Field(..., description="생성된 Authorization 헤더 값")

    class Config:
        json_schema_extra = {
            "example": {
                "Authorization": "client_id=HANJIN timestamp=20230607203623 signature=D68B0F9016310669C6BF6189590BA5D33F402612CDA0C6112C8F3ED628B4C04D"
            }
        }


class HmacErrorResponse(BaseModel):
    """HMAC 인증 에러 응답 스키마"""
    error_code: str = Field(..., description="에러 코드")
    message: str = Field(..., description="에러 메시지")

    class Config:
        json_schema_extra = {
            "example": {
                "error_code": "INVALID_CLIENT_ID",
                "message": "Invalid client_id provided"
            }
        }
