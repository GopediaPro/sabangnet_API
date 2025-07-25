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
# file
from minio_handler import upload_file_to_minio, get_minio_file_url


logger = get_logger(__name__)


router = APIRouter(
    prefix="/product",
    tags=["product"],
)


def get_product_read_service(session: AsyncSession = Depends(get_async_session)) -> ProductReadService:
    return ProductReadService(session=session)


def get_product_update_service(session: AsyncSession = Depends(get_async_session)) -> ProductUpdateService:
    return ProductUpdateService(session=session)


def get_product_db_xml_usecase(session: AsyncSession = Depends(get_async_session)) -> ProductDbXmlUsecase:
    return ProductDbXmlUsecase(session=session)


@router.post("/db-to-xml-all/sabangnet-request", response_model=DbToXmlResponse)
async def db_to_xml_sabangnet_request_all(
    product_db_xml_usecase: ProductDbXmlUsecase = Depends(get_product_db_xml_usecase)
):
    """
    test_product_raw_data 테이블의 모든 데이터를 XML로 변환하고 사방넷 상품등록 요청
    """
    try:
        # DB to XML 파일 로컬 저장
        xml_file_path = await product_db_xml_usecase.db_to_xml_file_all()
        total_count = await product_db_xml_usecase.get_product_raw_data_count()

        # 파일 서버 업로드
        object_name = upload_file_to_minio(xml_file_path)
        logger.info(f"MinIO에 업로드된 XML 파일 이름: {object_name}")
        xml_url = get_minio_file_url(object_name)
        logger.info(f"MinIO에 업로드된 XML URL: {xml_url}")

        # 해당 파일을 사방넷 상품등록 요청 후 결과 값 중 PRODUCT_ID 값 db 에 저장.
        response_xml = ProductCreateService.request_product_create_via_url(xml_url)
        logger.info(f"사방넷 상품등록 결과: {response_xml}")
        product_registration_xml = ProductRegistrationXml()
        compayny_goods_cd_and_product_ids: list[tuple[str, int]] = product_registration_xml.input_product_id_to_db(response_xml)
        await product_db_xml_usecase.update_product_id_by_compayny_goods_cd(compayny_goods_cd_and_product_ids)

        return DbToXmlResponse(
            success=True,
            message="모든 상품 데이터를 XML로 변환하고 사방넷 상품등록 요청했습니다.",
            xml_file_path=xml_url,
            processed_count=total_count
        )
    
    except ValueError as e:
        logger.warning(f"DB to XML 변환 실패 (데이터 없음): {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"DB to XML 변환 중 오류: {e}")
        raise HTTPException(status_code=500, detail=f"DB to XML 변환 중 오류가 발생했습니다: {str(e)}")


@router.post("/excel-to-xml-n8n-test", response_model=dict)
async def excel_to_xml_n8n_test(request: Request):
    file_name = None
    sheet_name = None
    try:
        data: dict = await request.json()
        file_name = data.get("fileName")
        sheet_name = data.get("sheetName")
        if not file_name:
            raise HTTPException(
                status_code=404, detail="대상 파일명을 입력해주세요. (예: OK_test_디자인업무일지)")
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
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=404, detail=f"파일을 찾을 수 없습니다. (파일명: {file_name} | 오류: {str(exc)})")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"오류가 발생했습니다. (파일명: {file_name} | 오류: {str(exc)})")


@router.put("/name", response_model=ProductNameResponse)
async def modify_product_name(
    request: ModifyProductNameForm,
    product_update_service: ProductUpdateService = Depends(get_product_update_service)
):
    try:
        return ProductNameResponse.from_dto(await product_update_service.modify_product_name(
            compayny_goods_cd=request.compayny_goods_cd,
            product_name=request.name
        ))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=ProductPageResponse)
async def get_products(
    page: int = Query(1, ge=1),
    product_read_service: ProductReadService = Depends(get_product_read_service)
):
    try:
        return ProductPageResponse.builder(
            products=[ProductResponse.from_dto(product) for product in await product_read_service.get_products_by_pagenation(page=page)],
            current_page=page,
            page_size=20
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bulk/db-to-excel", response_class=StreamingResponse)
async def bulk_db_to_excel(
    product_read_service: ProductReadService = Depends(get_product_read_service)
) -> StreamingResponse:
    return await product_read_service.convert_product_data_to_excel()