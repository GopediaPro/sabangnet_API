"""
Product Registration API
상품 등록 관련 API 엔드포인트
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import os
import logging

from core.db import get_async_session
from services.product_registration import ProductRegistrationService, ProductCodeIntegratedService
from schemas.product_registration import (
    ProductRegistrationBulkResponseDto,
    ProductRegistrationBulkCreateDto,
    ProductRegistrationResponseDto,
    ProductRegistrationCreateDto,
    ExcelProcessResultDto,
    ExcelImportResponseDto,
    CompleteWorkflowResponseDto
)
from utils.decorators import (
    product_registration_handler, 
    complete_workflow_handler,
    process_excel_file_with_cleanup
)
from utils.exceptions.http_exceptions import (
    ValidationException,
    NotFoundException,
    FileNotFoundException,
    DataNotFoundException,
    ProductRegistrationException
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

logger.info("Product Registration API 엔드포인트 로드 시작...")

# 스키마 로드 검증
try:
    logger.info("Product Registration 스키마 검증 중...")
    from schemas.product_registration import (
        ProductRegistrationBulkResponseDto,
        ProductRegistrationBulkCreateDto,
        ProductRegistrationResponseDto,
        ProductRegistrationCreateDto,
        ExcelProcessResultDto,
        ExcelImportResponseDto,
        CompleteWorkflowResponseDto
    )
    logger.info("Product Registration 스키마 로드 성공")
except Exception as e:
    logger.error(f"Product Registration 스키마 로드 실패: {e}")
    import traceback
    logger.error(traceback.format_exc())

router = APIRouter(
    prefix="/product-registration",
    tags=["product-registration"]
)

logger.info("Product Registration 라우터 생성 완료")


async def get_product_registration_service(
    session: AsyncSession = Depends(get_async_session)
) -> ProductRegistrationService:
    """상품 등록 서비스 의존성 주입"""
    return ProductRegistrationService(session)


async def get_product_integrated_service() -> ProductCodeIntegratedService:
    """상품 등록 통합 서비스 의존성 주입"""
    return ProductCodeIntegratedService()


@router.get("/", summary="상품 등록 API 상태 확인")
async def get_api_status():
    """API 상태를 확인합니다."""
    return {"message": "Product Registration API is running", "status": "ok"}


@router.post(
    "/excel/process",
    response_model=ExcelProcessResultDto,
    summary="Excel 파일 처리",
    description="Excel 파일을 업로드하여 K:AZ 컬럼 데이터를 처리합니다."
)
@product_registration_handler
async def process_excel_file(
    file: UploadFile = File(..., description="처리할 Excel 파일"),
    sheet_name: str = Query("Sheet1", description="처리할 시트명"),
    service: ProductRegistrationService = Depends(get_product_registration_service)
):
    """Excel 파일을 처리하여 데이터를 검증합니다."""
    
    # Excel 파일 처리 및 정리 함수 가져오기
    process_file = process_excel_file_with_cleanup()
    temp_file_path, cleanup_func = process_file(file)
    
    try:
        # Excel 파일 처리
        result = await service.process_excel_file(temp_file_path, sheet_name)
        
        logger.info(f"Excel 파일 처리 완료: {file.filename}")
        return result
        
    finally:
        # 임시 파일 정리
        cleanup_func()


@router.post(
    "/excel/import",
    response_model=ExcelImportResponseDto,
    summary="Excel 파일 가져오기 및 DB 저장",
    description="Excel 파일을 처리하여 바로 데이터베이스에 저장합니다."
)
@product_registration_handler
async def import_excel_to_db(
    file: UploadFile = File(..., description="가져올 Excel 파일"),
    sheet_name: str = Query("Sheet1", description="처리할 시트명"),
    service: ProductRegistrationService = Depends(get_product_registration_service)
):
    """
    디자인업무일지.xlsx 파일의 '상품등록' 시트를 처리하여 데이터베이스에 저장합니다.
    데이터베이스에 저장된 데이터를 조회하여 반환합니다.
    """
    
    # Excel 파일 처리 및 정리 함수 가져오기
    process_file = process_excel_file_with_cleanup()
    temp_file_path, cleanup_func = process_file(file)
    
    try:
        # Excel 파일 처리 및 DB 저장
        excel_result, bulk_result = await service.process_excel_and_create(temp_file_path, sheet_name)
        
        logger.info(f"Excel 파일 가져오기 완료: {file.filename}")
        return ExcelImportResponseDto(
            message="Excel 파일 가져오기 완료",
            excel_processing=excel_result,
            database_result=bulk_result
        )
        
    finally:
        # 임시 파일 정리
        cleanup_func()


@router.post(
    "/complete-workflow",
    response_model=CompleteWorkflowResponseDto,
    summary="전체 상품 등록 워크플로우",
    description="Excel 파일 처리부터 사방넷 API 요청까지의 전체 프로세스를 한 번에 처리합니다."
)
async def process_complete_workflow(
    file: UploadFile = File(..., description="처리할 Excel 파일"),
    sheet_name: str = Query("상품등록", description="처리할 시트명"),
    service: ProductCodeIntegratedService = Depends(get_product_integrated_service)
):
    """
    전체 상품 등록 워크플로우를 처리합니다:
    1. Excel 파일 처리 및 DB 저장
    2. DB Transfer (product_registration_raw_data → test_product_raw_data)
    3. DB to SabangAPI 요청
    """
    
    try:
        # Excel 파일 처리 및 정리 함수 가져오기
        process_file = process_excel_file_with_cleanup()
        temp_file_path, cleanup_func = process_file(file)
        
        try:
            # 전체 워크플로우 처리
            result = await service.process_complete_product_registration_workflow(
                temp_file_path, 
                sheet_name
            )
            
            logger.info(f"전체 워크플로우 완료: {file.filename}")
            return CompleteWorkflowResponseDto(**result)
            
        finally:
            # 임시 파일 정리
            cleanup_func()
            
    except ValueError as e:
        logger.error(f"전체 워크플로우 검증 오류: {str(e)}")
        raise ValidationException(str(e))
    except FileNotFoundError as e:
        logger.error(f"파일을 찾을 수 없음: {str(e)}")
        raise FileNotFoundException(str(e))
    except Exception as e:
        logger.error(f"전체 워크플로우 처리 오류: {str(e)}")
        
        # 오류 메시지에 추가 정보 포함
        error_message = f"전체 워크플로우 처리 중 오류가 발생했습니다. 오류: {str(e)}"
        
        # 로그에서 XML 파싱 오류나 API 응답 정보가 있는지 확인
        if "XML 파싱 오류" in str(e) or "unclosed token" in str(e):
            error_message += " (XML 파싱 오류가 발생했습니다. 사방넷 API 응답을 확인해주세요.)"
        
        if "상품등록 결과 XML 파싱 오류" in str(e):
            error_message += " (사방넷 API에서 반환된 XML 응답을 파싱할 수 없습니다.)"
        
        # 전체 오류 메시지를 로그에 기록
        logger.error(f"전체 오류 메시지: {error_message}")
            
        raise ProductRegistrationException(error_message)


@router.post(
    "/local-excel/import",
    response_model=ExcelImportResponseDto,
    summary="로컬 Excel 파일 가져오기",
    description="서버의 로컬 Excel 파일을 처리하여 데이터베이스에 저장합니다."
)
@product_registration_handler
async def import_local_excel_to_db(
    file_path: str = Query(..., description="처리할 Excel 파일 경로"),
    sheet_name: str = Query("Sheet1", description="처리할 시트명"),
    service: ProductRegistrationService = Depends(get_product_registration_service)
):
    """로컬 Excel 파일을 처리하여 데이터베이스에 저장합니다."""
    
    # 파일 존재 확인
    if not os.path.exists(file_path):
        raise FileNotFoundException(file_path)
    
    # Excel 파일 확장자 확인
    if not file_path.endswith(('.xlsx', '.xls')):
        raise ValidationException("Excel 파일만 처리 가능합니다. (.xlsx, .xls)")
    
    # Excel 파일 처리 및 DB 저장
    excel_result, bulk_result = await service.process_excel_and_create(file_path, sheet_name)
    
    logger.info(f"로컬 Excel 파일 가져오기 완료: {file_path}")
    return ExcelImportResponseDto(
        message="로컬 Excel 파일 가져오기 완료",
        excel_processing=excel_result,
        database_result=bulk_result
    )


@router.post(
    "/create",
    response_model=ProductRegistrationResponseDto,
    summary="단일 상품 등록",
    description="단일 상품 등록 데이터를 생성합니다."
)
@product_registration_handler
async def create_single_product(
    data: ProductRegistrationCreateDto,
    service: ProductRegistrationService = Depends(get_product_registration_service)
):
    """단일 상품 등록 데이터를 생성합니다."""
    result = await service.create_single_product(data)
    logger.info(f"단일 상품 등록 완료: ID={result.id}")
    return result


@router.post(
    "/bulk-create",
    response_model=ProductRegistrationBulkResponseDto,
    summary="대량 상품 등록",
    description="여러 상품 등록 데이터를 한 번에 생성합니다."
)
@product_registration_handler
async def create_bulk_products(
    data: ProductRegistrationBulkCreateDto,
    service: ProductRegistrationService = Depends(get_product_registration_service)
):
    """대량 상품 등록 데이터를 생성합니다."""
    result = await service.create_bulk_products(data.data)
    logger.info(f"대량 상품 등록 완료: 성공 {result.success_count}개")
    return result


@router.get(
    "/list",
    response_model=List[ProductRegistrationResponseDto],
    summary="상품 등록 데이터 목록 조회",
    description="상품 등록 데이터 목록을 조회합니다."
)
@product_registration_handler
async def get_products_list(
    limit: int = Query(100, ge=1, le=1000, description="조회할 데이터 수"),
    offset: int = Query(0, ge=0, description="조회 시작 위치"),
    service: ProductRegistrationService = Depends(get_product_registration_service)
):
    """상품 등록 데이터 목록을 조회합니다."""
    result = await service.get_products_list(limit, offset)
    return result


@router.get(
    "/{product_id}",
    response_model=ProductRegistrationResponseDto,
    summary="상품 등록 데이터 단일 조회",
    description="ID로 상품 등록 데이터를 조회합니다."
)
@product_registration_handler
async def get_product_by_id(
    product_id: int,
    service: ProductRegistrationService = Depends(get_product_registration_service)
):
    """ID로 상품 등록 데이터를 조회합니다."""
    result = await service.get_product_by_id(product_id)
    if not result:
        raise DataNotFoundException("상품 등록 데이터를 찾을 수 없습니다.")
    return result


@router.get(
    "/search/",
    response_model=List[ProductRegistrationResponseDto],
    summary="상품 등록 데이터 검색",
    description="제품명이나 상품명으로 데이터를 검색합니다."
)
@product_registration_handler
async def search_products(
    q: str = Query(..., min_length=1, description="검색어 (제품명, 상품명)"),
    limit: int = Query(50, ge=1, le=200, description="조회할 데이터 수"),
    service: ProductRegistrationService = Depends(get_product_registration_service)
):
    """제품명이나 상품명으로 데이터를 검색합니다."""
    result = await service.search_products(q, limit)
    return result


@router.put(
    "/{product_id}",
    response_model=ProductRegistrationResponseDto,
    summary="상품 등록 데이터 업데이트",
    description="ID로 상품 등록 데이터를 업데이트합니다."
)
@product_registration_handler
async def update_product(
    product_id: int,
    data: ProductRegistrationCreateDto,
    service: ProductRegistrationService = Depends(get_product_registration_service)
):
    """ID로 상품 등록 데이터를 업데이트합니다."""
    result = await service.update_product(product_id, data)
    if not result:
        raise DataNotFoundException("상품 등록 데이터를 찾을 수 없습니다.")
    
    logger.info(f"상품 업데이트 완료: ID={product_id}")
    return result


@router.delete(
    "/{product_id}",
    summary="상품 등록 데이터 삭제",
    description="ID로 상품 등록 데이터를 삭제합니다."
)
@product_registration_handler
async def delete_product(
    product_id: int,
    service: ProductRegistrationService = Depends(get_product_registration_service)
):
    """ID로 상품 등록 데이터를 삭제합니다."""
    deleted = await service.delete_product(product_id)
    if not deleted:
        raise DataNotFoundException("상품 등록 데이터를 찾을 수 없습니다.")
    
    logger.info(f"상품 삭제 완료: ID={product_id}")
    return {"message": "상품 등록 데이터가 성공적으로 삭제되었습니다.", "deleted_id": product_id}
