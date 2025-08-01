# std
import requests
from pathlib import Path
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
from schemas.product.db_xml_dto import DbToXmlResponse
from schemas.product.request.product_form import ModifyProductNameForm
from schemas.product.response.product_response import (
    ProductPageResponse,
    ProductNameResponse,
    ProductResponse,
)
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
from minio_handler import upload_file_to_minio, get_minio_file_url


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
    prefix="/product",
    tags=["product"],
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


@router.post("/db-to-xml-all/sabangnet-request", response_model=DbToXmlResponse)
@product_handler
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


@router.post("/excel-to-xml-n8n-test", response_model=dict)
@product_handler
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


@router.put("/name", response_model=ProductNameResponse)
@product_handler
async def modify_product_name(
    request: ModifyProductNameForm,
    product_update_service: ProductUpdateService = Depends(get_product_update_service)
):
    return ProductNameResponse.from_dto(await product_update_service.modify_product_name(
        compayny_goods_cd=request.compayny_goods_cd,
        product_name=request.name
    ))


@router.get("", response_model=ProductPageResponse)
@product_handler
async def get_products(
    page: int = Query(1, ge=1),
    product_read_service: ProductReadService = Depends(get_product_read_service)
):
    return ProductPageResponse.builder(
        products=[ProductResponse.from_dto(product) for product in await product_read_service.get_products_by_pagenation(page=page)],
        current_page=page,
        page_size=20
    )


@router.get("/bulk/db-to-excel", response_class=StreamingResponse)
@product_handler
async def bulk_db_to_excel(
    product_read_service: ProductReadService = Depends(get_product_read_service)
) -> StreamingResponse:
    return await product_read_service.convert_product_data_to_excel()