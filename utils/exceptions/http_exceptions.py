"""
공통 HTTPException 처리를 위한 예외 클래스들
"""

from fastapi import HTTPException
from typing import Optional, Dict, Any


class BaseHTTPException(HTTPException):
    """기본 HTTPException 클래스"""
    
    def __init__(
        self,
        status_code: int,
        error_code: str,
        message: str,
        detail: Optional[Dict[str, Any]] = None
    ):
        self.error_code = error_code
        self.detail_dict = {
            "error_code": error_code,
            "message": message
        }
        if detail:
            self.detail_dict.update(detail)
        
        super().__init__(status_code=status_code, detail=self.detail_dict)


class ValidationException(BaseHTTPException):
    """검증 오류 예외"""
    
    def __init__(self, message: str, detail: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=400,
            error_code="VALIDATION_ERROR",
            message=message,
            detail=detail
        )


class NotFoundException(BaseHTTPException):
    """리소스를 찾을 수 없음 예외"""
    
    def __init__(self, message: str, detail: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=404,
            error_code="NOT_FOUND",
            message=message,
            detail=detail
        )


class FileNotFoundException(NotFoundException):
    """파일을 찾을 수 없음 예외"""
    
    def __init__(self, file_name: str, detail: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"파일을 찾을 수 없습니다: {file_name}",
            detail=detail
        )


class DataNotFoundException(NotFoundException):
    """데이터를 찾을 수 없음 예외"""
    
    def __init__(self, message: str, detail: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            detail=detail
        )


class InternalServerException(BaseHTTPException):
    """내부 서버 오류 예외"""
    
    def __init__(self, message: str, detail: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=500,
            error_code="INTERNAL_SERVER_ERROR",
            message=message,
            detail=detail
        )


class ProductException(BaseHTTPException):
    """상품 관련 예외"""
    
    def __init__(self, message: str, detail: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=500,
            error_code="PRODUCT_ERROR",
            message=message,
            detail=detail
        )


class ProductRegistrationException(BaseHTTPException):
    """상품 등록 관련 예외"""
    
    def __init__(self, message: str, detail: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=500,
            error_code="PRODUCT_REGISTRATION_ERROR",
            message=message,
            detail=detail
        )


class HanjinException(BaseHTTPException):
    """한진 API 관련 예외"""
    
    def __init__(self, message: str, detail: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=500,
            error_code="HANJIN_API_ERROR",
            message=message,
            detail=detail
        )


class SmileException(BaseHTTPException):
    """스마일배송 관련 예외"""
    
    def __init__(self, message: str, detail: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=500,
            error_code="SMILE_EXCEL_IMPORT_ERROR",
            message=message,
            detail=detail
        )


# 편의 함수들
def raise_validation_error(message: str, detail: Optional[Dict[str, Any]] = None):
    """검증 오류를 발생시킵니다."""
    raise ValidationException(message, detail)


def raise_not_found_error(message: str, detail: Optional[Dict[str, Any]] = None):
    """리소스를 찾을 수 없음 오류를 발생시킵니다."""
    raise NotFoundException(message, detail)


def raise_file_not_found_error(file_name: str, detail: Optional[Dict[str, Any]] = None):
    """파일을 찾을 수 없음 오류를 발생시킵니다."""
    raise FileNotFoundException(file_name, detail)


def raise_data_not_found_error(message: str, detail: Optional[Dict[str, Any]] = None):
    """데이터를 찾을 수 없음 오류를 발생시킵니다."""
    raise DataNotFoundException(message, detail)


def raise_internal_server_error(message: str, detail: Optional[Dict[str, Any]] = None):
    """내부 서버 오류를 발생시킵니다."""
    raise InternalServerException(message, detail) 