from fastapi import status
from datetime import datetime, timezone
from typing import Optional, TypeVar
from pydantic import BaseModel, Field
from fastapi.responses import JSONResponse


# 제네릭 타입 변수 정의
T = TypeVar('T')


class Metadata(BaseModel):
    version: str = Field(..., description="버전")
    request_id: Optional[str] = Field(None, description="요청 ID")

    class Config:
        from_attributes = True


# 성공 응답
class SuccessResponse(BaseModel):
    success: bool = True
    data: T = Field(..., description="데이터")
    metadata: Metadata = Field(..., description="메타데이터")

    class Config:
        from_attributes = True

    
# 실패 응답
class ErrorDetails(BaseModel):
    field: str = Field(..., description="필드")
    message: str = Field(..., description="메시지")

    class Config:
        from_attributes = True


class Error(BaseModel):
    code: str = Field(..., description="코드")
    message: str = Field(..., description="메시지")
    details: Optional[list[ErrorDetails]] = Field(None, description="상세 정보")

    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    success: bool = Field(..., description="성공 여부")
    error: Error = Field(..., description="에러 정보")
    metadata: Metadata = Field(..., description="메타데이터")

    class Config:
        from_attributes = True

# Response Handler 클래스
class ResponseHandler:
    
    @staticmethod
    def success(
        success_response: SuccessResponse,
        status_code: int,
    ) -> JSONResponse:
        """성공 응답 생성"""
        response_data = {
            "success": success_response.success,
            "data": success_response.data.model_dump(mode="json") if isinstance(success_response.data, BaseModel) else success_response.data,
            "metadata": success_response.metadata.model_dump(mode="json"),
        }
        
        return JSONResponse(
            content=response_data,
            status_code=status_code
        )
    
    @staticmethod
    def error(
        error_response: ErrorResponse,
        status_code: int,
    ) -> JSONResponse:
        """에러 응답 생성"""
        response_data = {
            "success": error_response.success,
            "error": error_response.error.model_dump(mode="json"),
            "metadata": error_response.metadata.model_dump(mode="json"),
        }
        
        return JSONResponse(
            content=response_data,
            status_code=status_code
        )

    # 편의 메서드들
    @staticmethod
    def ok(data: T, metadata: Metadata) -> JSONResponse:
        """200 OK 응답"""
        return ResponseHandler.success(SuccessResponse(success=True, data=data, metadata=metadata), status.HTTP_200_OK)
    
    @staticmethod
    def created(data: T, metadata: Metadata) -> JSONResponse:
        """201 Created 응답"""
        return ResponseHandler.success(SuccessResponse(success=True, data=data, metadata=metadata), status.HTTP_201_CREATED)
    
    @staticmethod
    def no_content(metadata: Metadata) -> JSONResponse:
        """204 No Content 응답"""
        return ResponseHandler.success(SuccessResponse(success=True, data={}, metadata=metadata), status.HTTP_204_NO_CONTENT)
    
    @staticmethod
    def bad_request(message: str, metadata: Metadata, details: Optional[list[ErrorDetails]] = None) -> JSONResponse:
        """400 Bad Request 응답"""
        error = Error(
            code="BAD_REQUEST",
            message=message,
            details=details
        )
        return ResponseHandler.error(
            ErrorResponse(
                success=False,
                error=error,
                metadata=metadata
            ),
            status.HTTP_400_BAD_REQUEST
        )
    
    @staticmethod
    def unauthorized(message: str, metadata: Metadata, details: Optional[list[ErrorDetails]] = None) -> JSONResponse:
        """401 Unauthorized 응답"""
        error = Error(
            code="UNAUTHORIZED",
            message=message,
            details=details
        )
        return ResponseHandler.error(
            ErrorResponse(
                success=False,
                error=error,
                metadata=metadata
            ),
            status.HTTP_401_UNAUTHORIZED
        )
    
    @staticmethod
    def forbidden(message: str, metadata: Metadata, details: Optional[list[ErrorDetails]] = None) -> JSONResponse:
        """403 Forbidden 응답"""
        error = Error(
            code="FORBIDDEN",
            message=message,
            details=details
        )
        return ResponseHandler.error(
            ErrorResponse(
                success=False,
                error=error,
                metadata=metadata
            ),
            status.HTTP_403_FORBIDDEN
        )
    
    @staticmethod
    def not_found(message: str, metadata: Metadata, details: Optional[list[ErrorDetails]] = None) -> JSONResponse:
        """404 Not Found 응답"""
        error = Error(
            code="NOT_FOUND",
            message=message,
            details=details
        )
        return ResponseHandler.error(
            ErrorResponse(
                success=False,
                error=error,
                metadata=metadata
            ),
            status.HTTP_404_NOT_FOUND
        )
    
    @staticmethod
    def validation_error(message: str, metadata: Metadata, details: Optional[list[ErrorDetails]] = None) -> JSONResponse:
        """422 Validation Error 응답"""
        error = Error(
            code="VALIDATION_ERROR",
            message=message,
            details=details
        )
        return ResponseHandler.error(
            ErrorResponse(
                success=False,
                error=error,
                metadata=metadata
            ),
            status.HTTP_422_UNPROCESSABLE_ENTITY
        )
    
    @staticmethod
    def internal_error(message: str, metadata: Metadata, details: Optional[list[ErrorDetails]] = None) -> JSONResponse:
        """500 Internal Server Error 응답"""
        error = Error(
            code="INTERNAL_ERROR",
            message=message,
            details=details
        )
        return ResponseHandler.error(
            ErrorResponse(
                success=False,
                error=error,
                metadata=metadata
            ), status.HTTP_500_INTERNAL_SERVER_ERROR)
