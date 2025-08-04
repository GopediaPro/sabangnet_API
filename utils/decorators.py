import functools
from fastapi import HTTPException, Depends
from typing import Optional, Any
from utils.logs.sabangnet_logger import get_logger
from utils.exceptions.http_exceptions import (
    ValidationException,
    NotFoundException,
    FileNotFoundException,
    DataNotFoundException,
    InternalServerException,
    ProductException,
    ProductRegistrationException,
    HanjinException,
    SmileException
)
from minio_handler import temp_file_to_object_name, delete_temp_file

def api_exception_handler(logger=None, default_status=500, default_detail="Internal Server Error"):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except HTTPException:
                raise
            except Exception as e:
                if logger:
                    logger.error(f"{func.__name__} error: {e}")
                raise HTTPException(status_code=default_status, detail=f"{default_detail}: {str(e)}")
        return wrapper
    return decorator


def hanjin_api_handler(
    error_code: str = "HANJIN_API_ERROR",
    error_message: str = "한진 API 요청 중 오류가 발생했습니다."
):
    """
    한진 API 요청을 위한 공통 핸들러 데코레이터
    
    Args:
        error_code: 에러 코드
        error_message: 기본 에러 메시지
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            logger = get_logger(__name__)
            try:
                return await func(*args, **kwargs)
            except ValueError as e:
                logger.error(f"한진 API 검증 오류: {str(e)}")
                raise ValidationException(str(e))
            except Exception as e:
                logger.error(f"한진 API 요청 오류: {str(e)}")
                raise HanjinException(error_message)
        return wrapper
    return decorator


def validate_hanjin_env_vars():
    """
    한진 API 환경변수 검증을 위한 의존성 함수
    """
    from core.settings import SETTINGS
    
    if not SETTINGS.HANJIN_API:
        raise ValidationException("환경변수 HANJIN_API가 설정되지 않았습니다.")
    
    if not SETTINGS.HANJIN_CLIENT_ID:
        raise ValidationException("환경변수 HANJIN_CLIENT_ID가 설정되지 않았습니다.")
    
    return True


def smile_excel_import_handler(
    error_code: str = "SMILE_EXCEL_IMPORT_ERROR",
    error_message: str = "스마일배송 Excel 가져오기 중 오류가 발생했습니다."
):
    """
    스마일배송 Excel 가져오기 API 요청을 위한 공통 핸들러 데코레이터
    
    Args:
        error_code: 에러 코드
        error_message: 기본 에러 메시지
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            logger = get_logger(__name__)
            try:
                return await func(*args, **kwargs)
            except ValueError as e:
                logger.error(f"스마일배송 Excel 가져오기 검증 오류: {str(e)}")
                raise ValidationException(str(e))
            except Exception as e:
                logger.error(f"스마일배송 Excel 가져오기 오류: {str(e)}")
                raise SmileException(error_message)
        return wrapper
    return decorator


def validate_excel_file(file):
    """Excel 파일 검증"""
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise ValidationException("Excel 파일만 업로드 가능합니다. (.xlsx, .xls)")
    return file


def process_excel_file_with_cleanup():
    """
    Excel 파일 처리 및 정리를 위한 유틸리티 함수
    """
    def process_file(file):
        # Excel 파일 검증
        validate_excel_file(file)
        
        # 임시 파일로 저장
        temp_file_path = temp_file_to_object_name(file)
        
        return temp_file_path, lambda: delete_temp_file(temp_file_path)
    
    return process_file


def product_registration_handler(
    error_code: str = "PRODUCT_REGISTRATION_ERROR",
    error_message: str = "상품 등록 처리 중 오류가 발생했습니다."
):
    """
    상품 등록 API 요청을 위한 공통 핸들러 데코레이터
    
    Args:
        error_code: 에러 코드
        error_message: 기본 에러 메시지
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            logger = get_logger(__name__)
            try:
                return await func(*args, **kwargs)
            except ValueError as e:
                logger.error(f"상품 등록 검증 오류: {str(e)}")
                raise ValidationException(str(e))
            except Exception as e:
                logger.error(f"상품 등록 처리 오류: {str(e)}")
                raise ProductRegistrationException(error_message)
        return wrapper
    return decorator


def complete_workflow_handler(
    error_code: str = "COMPLETE_WORKFLOW_ERROR",
    error_message: str = "전체 워크플로우 처리 중 오류가 발생했습니다."
):
    """
    전체 워크플로우 API 요청을 위한 공통 핸들러 데코레이터
    
    Args:
        error_code: 에러 코드
        error_message: 기본 에러 메시지
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            logger = get_logger(__name__)
            try:
                return await func(*args, **kwargs)
            except ValueError as e:
                logger.error(f"전체 워크플로우 검증 오류: {str(e)}")
                raise ValidationException(str(e))
            except FileNotFoundError as e:
                logger.error(f"파일을 찾을 수 없음: {str(e)}")
                raise FileNotFoundException(str(e))
            except Exception as e:
                logger.error(f"전체 워크플로우 처리 오류: {str(e)}")
                raise ProductRegistrationException(error_message)
        return wrapper
    return decorator


def product_handler(
    error_code: str = "PRODUCT_ERROR",
    error_message: str = "상품 처리 중 오류가 발생했습니다."
):
    """
    상품 API 요청을 위한 공통 핸들러 데코레이터
    
    Args:
        error_code: 에러 코드
        error_message: 기본 에러 메시지
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            logger = get_logger(__name__)
            try:
                return await func(*args, **kwargs)
            except ValueError as e:
                logger.error(f"상품 검증 오류: {str(e)}")
                raise ValidationException(str(e))
            except FileNotFoundError as e:
                logger.error(f"파일을 찾을 수 없음: {str(e)}")
                raise FileNotFoundException(str(e))
            except Exception as e:
                logger.error(f"상품 처리 오류: {str(e)}")
                raise ProductException(error_message)
        return wrapper
    return decorator 