"""
Product API
기존의 '품번코드대량등록툴' 이라는 엑셀 시트와 관련된 API 엔드포인트
"""

# std
import requests
from pathlib import Path
from typing import Optional
import os
# core
from core.settings import SETTINGS
from core.db import get_async_session
# fastapi
from fastapi.responses import StreamingResponse
from fastapi import APIRouter, Depends, HTTPException, Query, Request
# services
from services.product.product_read_service import ProductReadService
from services.product.product_create_service import ProductCreateService
from services.product.product_update_service import ProductUpdateService
from services.usecase.product_db_xml_usecase import ProductDbXmlUsecase
from services.product_registration.product_registration_service import ProductRegistrationService
# schemas
from schemas.integration_response import ResponseHandler, Metadata
from schemas.product.db_xml_dto import DbToXmlResponse
from schemas.product.request.product_form import ModifyProductNameForm
from schemas.product.response.product_response import (
    ProductPageResponse,
    ProductNameResponse,
    ProductResponse,
)
from schemas.product_registration import (
    ProductDbToExcelResponse,
    ProductDbToExcelRequest,
)
from schemas.integration_request import IntegrationRequest
from schemas.product_registration.docs_succes_integration_responses import SuccessResponseSchema
# sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession
# utils
from utils.logs.sabangnet_logger import get_logger
from utils.make_xml.product_registration_xml import ProductRegistrationXml
from utils.decorators import product_handler
from utils.exceptions.http_exceptions import (
    ValidationException,
    NotFoundException,
    FileNotFoundException,
    DataNotFoundException
)
# file
from minio_handler import upload_file_to_minio, get_minio_file_url, upload_and_get_url_and_size, url_arrange


logger = get_logger(__name__)

logger.info("Product API 엔드포인트 로드 시작...")

# 스키마 로드 검증
try:
    logger.info("Product 스키마 검증 중...")
    from schemas.product.db_xml_dto import DbToXmlResponse
    from schemas.product.response.product_response import (
        ProductPageResponse,
        ProductNameResponse,
        ProductResponse,
    )
    logger.info("Product 스키마 로드 성공")
except Exception as e:
    logger.error(f"Product 스키마 로드 실패: {e}")
    import traceback
    logger.error(traceback.format_exc())


router = APIRouter(
    prefix="/product-bulk-tool",
    tags=["product-bulk-tool"],
)

logger.info("Product 라우터 생성 완료")


def get_product_read_service(session: AsyncSession = Depends(get_async_session)) -> ProductReadService:
    return ProductReadService(session=session)


def get_product_update_service(session: AsyncSession = Depends(get_async_session)) -> ProductUpdateService:
    return ProductUpdateService(session=session)


def get_product_db_xml_usecase(session: AsyncSession = Depends(get_async_session)) -> ProductDbXmlUsecase:
    return ProductDbXmlUsecase(session=session)


def get_product_registration_service(session: AsyncSession = Depends(get_async_session)) -> ProductRegistrationService:
    return ProductRegistrationService(session=session)


@router.get("/all", response_model=ProductPageResponse)
@product_handler()
async def get_products_all(
    skip: int = Query(0, ge=0, description="건너뛸 건수"),
    limit: int = Query(200, ge=1, description="조회할 건수"),
    product_read_service: ProductReadService = Depends(get_product_read_service)
):
    return ProductPageResponse.builder(
        products=[ProductResponse.from_dto(product) for product in await product_read_service.get_products_all(skip=skip, limit=limit)],
        current_page=1,
        page_size=10000
    )


@router.get("/pagenation", response_model=ProductPageResponse)
@product_handler()
async def get_products_by_pagenation(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=1000), # 기본 20건
    product_read_service: ProductReadService = Depends(get_product_read_service)
):
    return ProductPageResponse.builder(
        products=[ProductResponse.from_dto(product) for product in await product_read_service.get_products_by_pagenation(page=page, page_size=page_size)],
        current_page=page,
        page_size=page_size
    )


@router.post("/db-to-xml-all/sabangnet-request", response_model=DbToXmlResponse)
@product_handler()
async def db_to_xml_sabangnet_request_all(
    product_registration_service: ProductRegistrationService = Depends(get_product_registration_service)
):
    """
    test_product_raw_data 테이블의 모든 데이터를 XML로 변환하고 사방넷 상품등록 요청
    """
    result = await product_registration_service.process_db_to_xml_and_sabangnet_request()
    
    return DbToXmlResponse(
        success=result["success"],
        message=result["message"],
        xml_file_path=result["xml_file_path"],
        processed_count=result["processed_count"]
    )


# 현재 사용 안함 (n8n 연동 중단 상태)
@router.post("/excel-to-xml-n8n-test", response_model=dict)
@product_handler()
async def excel_to_xml_n8n_test(request: Request):
    data: dict = await request.json()
    file_name = data.get("fileName")
    sheet_name = data.get("sheetName")
    
    if not file_name:
        raise ValidationException("대상 파일명을 입력해주세요. (예: OK_test_디자인업무일지)")
    
    xml_file_path: Path = ProductCreateService.excel_to_xml_file(
        file_name, sheet_name)
    
    with open(xml_file_path, 'rb') as f:
        files = {
            'file': (f'{xml_file_path}', f, 'application/xml')}
        data = {'filename': f'{xml_file_path}'}
        response = requests.post(
            f"{SETTINGS.N8N_WEBHOOK_BASE_URL}/{SETTINGS.N8N_WEBHOOK_PATH}",
            files=files,
            data=data
        )
        response.raise_for_status()
        result: dict = response.json()
        return result


@router.get("/bulk/db-to-excel", response_class=StreamingResponse)
@product_handler()
async def bulk_db_to_excel(
    product_read_service: ProductReadService = Depends(get_product_read_service)
) -> StreamingResponse:
    return await product_read_service.convert_product_data_to_excel()


@router.post(
    "/excel/db-to-excel",
    name="download_test_products_excel",
    response_model=SuccessResponseSchema[ProductDbToExcelResponse],
    summary="대량 상품 등록 데이터(test_product_raw_data) Excel 다운로드 URL 반환",
    description="대량 상품 등록 데이터(test_product_raw_data)를 Excel 파일로 생성 후 MinIO 업로드 URL과 메타데이터를 JSON으로 반환합니다. (정렬/날짜 필터링 지원)"
)
async def download_test_products_excel(
    request: IntegrationRequest[ProductDbToExcelRequest],
    service: "ProductReadService" = Depends(get_product_read_service),
):
    """
    - 서비스에서 test_product_raw_data 기반 Excel 파일 생성
    - MinIO 업로드 후 URL/레코드수/파일크기 반환
    - 업로드 후 임시파일 삭제
    """
    temp_path: Optional[str] = None
    try:
        # 1) Excel 파일 생성
        temp_path, file_name, record_count, file_size = await service.convert_test_product_data_to_excel_file_by_filter(
            sort_order=request.data.sort_order,
            created_before=request.data.created_before,
        )

        # 2) MinIO 업로드
        file_url, minio_object_name, uploaded_size = upload_and_get_url_and_size(
            temp_path,
            "test_product_excel",   # 버킷/경로명은 실제 정책에 맞게 지정
            file_name
        )
        file_url = url_arrange(file_url)

        logger.info(
            f"[download_test_products_excel] 업로드 완료 - URL: {file_url}, "
            f"레코드 수: {record_count}, 파일 크기(bytes): {uploaded_size}"
        )

        # 3) JSON 응답
        body = ProductDbToExcelResponse(
            excel_url=file_url,
            record_count=record_count,
            file_size=uploaded_size,
        )
        return ResponseHandler.ok(
            data=body,
            metadata=Metadata(version="v1", request_id=request.metadata.request_id or "N/A"),
        )

    except DataNotFoundException as e:
        logger.warning(f"[download_test_products_excel] 데이터 없음: {str(e)}")
        return ResponseHandler.internal_error(
            message=str(e),
            metadata=Metadata(version="v1", request_id=request.metadata.request_id or "N/A"),
        )
    except Exception as e:
        logger.error(f"[download_test_products_excel] 실패: {str(e)}")
        return ResponseHandler.internal_error(
            message=str(e),
            metadata=Metadata(version="v1", request_id=request.metadata.request_id or "N/A"),
        )
    finally:
        """4) 로컬 임시파일 정리"""
        try:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
        except Exception as cleanup_err:
            logger.warning(f"[download_test_products_excel] 임시파일 삭제 실패: {cleanup_err}")
