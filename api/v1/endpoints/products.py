# core
from core.settings import SETTINGS
from core.db import get_async_session

# fastapi
from fastapi import APIRouter, Depends, HTTPException, Query, Request

# python
import requests
from pathlib import Path

# repository
from repository.product_repository import ProductRepository

# services
from services.product.product_read_service import ProductReadService
from services.product.product_write_service import ProductWriteService
from services.product.product_create_service import ProductCreateService

# schemas
from schemas.product.request.product_form import ModifyProductNameForm
from schemas.product.response.product_response import ProductNameResponse, ProductResponse, ProductPageResponse

# sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession

# utils
from utils.sabangnet_logger import get_logger


logger = get_logger(__name__)


router = APIRouter(
    prefix="/products",
    tags=["products"],
)


def get_product_write_service(session: AsyncSession = Depends(get_async_session)) -> ProductWriteService:
    return ProductWriteService(session=session)


def get_product_read_service(session: AsyncSession = Depends(get_async_session)) -> ProductReadService:
    return ProductReadService(session=session)


@router.post("/excel-to-xml-n8n-test", response_model=dict)
async def excel_to_xml_n8n_test(request: Request):
    try:
        data: dict = await request.json()
        file_name = data.get("fileName")
        sheet_name = data.get("sheetName")
        if not file_name:
            raise HTTPException(
                status_code=400, detail="대상 파일명을 입력해주세요. (예: OK_test_디자인업무일지)")
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
    except FileNotFoundError as e:
        logger.error(f"파일을 찾을 수 없습니다. (파일명: {file_name} | 오류: {e})")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"오류가 발생했습니다. (파일명: {file_name} | 오류: {e})")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/name", response_model=ProductNameResponse)
async def modify_product_name(
    request: ModifyProductNameForm = Depends(),
    product_service: ProductWriteService = Depends(get_product_write_service)
):
    return ProductNameResponse.from_dto(await product_service.modify_product_name(
        compayny_goods_cd=request.compayny_goods_cd,
        product_name=request.name
    ))

@router.get("", response_model=ProductPageResponse)
async def get_products(
    page: int = Query(1, ge=1),
    product_service: ProductWriteService = Depends(get_product_write_service)
):
    return ProductPageResponse.builder(
        products=[ProductResponse.from_dto(product) for product in await product_service.get_products(page=page)],
        current_page=page,
        page_size=20
    )


@router.get("/bulk-register-db-to-excel")
async def bulk_register_db_to_excel(product_service: ProductReadService = Depends(get_product_read_service)):
    return await product_service.get_bulk_register_db_to_excel()


@router.get("/bulk-register-excel-to-db")
async def bulk_register_excel_to_db(product_service: ProductReadService = Depends(get_product_read_service)):
    return await product_service.get_bulk_register_excel_to_db()