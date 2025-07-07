# core
from core.settings import SETTINGS
from core.db import get_async_session, AsyncSessionLocal

# fastapi
from fastapi.responses import StreamingResponse
from fastapi import APIRouter, Depends, HTTPException, Query, Request

# python
import requests
from pathlib import Path

# services
from services.product.product_read_service import ProductReadService
from services.product.product_write_service import ProductWriteService
from services.product.product_create_service import ProductCreateService
from services.usecase.product_create_db_to_excel_usecase import ProductCreateDbToExcelUsecase

# schemas
from schemas.product.request.product_form import ModifyProductNameForm
from schemas.product.response.product_response import ProductNameResponse, ProductResponse, ProductPageResponse

# sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession

# utils
from schemas.product.db_xml_dto import DbToXmlResponse
from services.product.product_db_xml_service import ProductDbXmlService

from utils.sabangnet_logger import get_logger
from file_server_handler import upload_to_file_server, get_file_server_url
from utils.make_xml.product_registration_xml import ProductRegistrationXml

logger = get_logger(__name__)


router = APIRouter(
    prefix="/products",
    tags=["products"],
)


def get_product_write_service(session: AsyncSession = Depends(get_async_session)) -> ProductWriteService:
    return ProductWriteService(session=session)

@router.post("/db-to-xml-all", response_model=DbToXmlResponse)
async def db_to_xml_all():
    """
    test_product_raw_data 테이블의 모든 데이터를 XML로 변환
    """
    try:
        # DB to XML 파일 로컬 저장
        xml_file_path = await ProductDbXmlService.db_to_xml_file_all()
        total_count = await ProductDbXmlService.get_product_raw_data_count()
        # 파일 서버 업로드
        object_name = upload_to_file_server(xml_file_path)
        logger.info(f"파일 서버에 업로드된 XML 파일 이름: {object_name}")
        xml_url = get_file_server_url(object_name)
        logger.info(f"파일 서버에 업로드된 XML URL: {xml_url}")

        # 해당 파일을 사방넷 상품등록 요청 후 결과 값 중 PRODUCT_ID 값 db 에 저장.
        response_xml = ProductCreateService.request_product_create_via_url(xml_url)
        logger.info(f"사방넷 상품등록 결과: {response_xml}")
        async with AsyncSessionLocal() as session:
            await ProductRegistrationXml().input_product_id_to_db(response_xml, session)

        return DbToXmlResponse(
            success=True,
            message="모든 상품 데이터를 XML로 변환했습니다.",
            xml_file_path=xml_url,
            processed_count=total_count
        )
    
    except ValueError as e:
        logger.warning(f"DB to XML 변환 실패 (데이터 없음): {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"DB to XML 변환 중 오류: {e}")
        raise HTTPException(status_code=500, detail=f"DB to XML 변환 중 오류가 발생했습니다: {str(e)}")

def get_product_read_service(session: AsyncSession = Depends(get_async_session)) -> ProductReadService:
    return ProductReadService(session=session)


def get_product_create_db_to_excel_usecase(
    product_read_service: ProductReadService = Depends(get_product_read_service)
) -> ProductCreateDbToExcelUsecase:
    return ProductCreateDbToExcelUsecase(product_read_service=product_read_service)


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


@router.get("/bulk-register-db-to-excel", response_class=StreamingResponse)
async def bulk_register_db_to_excel(
    product_create_db_to_excel_usecase: ProductCreateDbToExcelUsecase = Depends(get_product_create_db_to_excel_usecase)
) -> StreamingResponse:
    return await product_create_db_to_excel_usecase.convert_db_to_excel()