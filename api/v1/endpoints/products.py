import requests

from pathlib import Path

from fastapi import Request

from core.settings import SETTINGS
from core.db import get_async_session

from repository.product_repository import ProductRepository

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, Depends, HTTPException

from services.product.product_create_service import ProductCreateService

from services.product.product_write_service import ProductWriteService
from schemas.product.request.product_form import ModifyProductNameForm
from schemas.product.response.product_response import ProductNameResponse

from utils.sabangnet_logger import get_logger


logger = get_logger(__name__)


router = APIRouter(
    prefix="/products",
    tags=["products"],
)


# 의존성 주입을 통해 ProductCRUD 인스턴스 생성
def get_product_crud(session: AsyncSession = Depends(get_async_session)) -> ProductRepository:
    return ProductRepository(session=session)


def get_product_write_service(session: AsyncSession = Depends(get_async_session)) -> ProductWriteService:
    return ProductWriteService(session=session)


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
