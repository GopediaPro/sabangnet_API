import requests

import xmltodict

from typing import List

from fastapi import Request

from core.settings import SETTINGS
from core.db import get_async_session

from crud.product_crud import ProductCRUD

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, Depends, HTTPException

from utils.sabangnet_formatter import SabangNetFormatter

from models.product.product_raw_data import ProductRawData
from models.product.modified_product_data import ModifiedProductData

router = APIRouter(
    prefix="/products",
    tags=["products"],
)


# 의존성 주입을 통해 ProductCRUD 인스턴스 생성
def get_product_crud(session: AsyncSession = Depends(get_async_session)) -> ProductCRUD:
    return ProductCRUD(session=session)


# @router.get("/raw", response_model=List[ProductRawData])
# async def read_products(skip: int = 0, limit: int = 10, product_crud: ProductCRUD = Depends(get_product_crud)):
#     items: List[ProductRawData] = await product_crud.get_unmodified_raws(skip=skip, limit=limit)
#     return items


# @router.post("/raw", response_model=ProductRawData)
# async def create_products(item: List[ProductRawData], product_crud: ProductCRUD = Depends(get_product_crud)):
#     items: List[ProductRawData] = await product_crud.product_raw_data_create(item=item)
#     return items


# @router.get("/modified", response_model=List[ModifiedProductData])
# async def read_modified_products(skip: int = 0, limit: int = 10, product_crud: ProductCRUD = Depends(get_product_crud)):
#     items: List[ModifiedProductData] = await product_crud.get_modified_raws(skip=skip, limit=limit)
#     return items


# @router.post("/modified", response_model=ModifiedProductData)
# async def create_modified_products(item: ModifiedProductData, product_crud: ProductCRUD = Depends(get_product_crud)):
#     ...


@router.post("/xlsx-to-xml", response_model=dict)
async def xlsx_to_xml(request: Request):
    try:
        data: dict = await request.json()
        # target = "OK_test_디자인업무일지"
        target = data.get("data")
        if not target:
            raise HTTPException(status_code=400, detail="대상 파일명을 입력해주세요. (예: OK_test_디자인업무일지)")
        formatter = SabangNetFormatter()
        xml_content = formatter.xlsx_to_xml(target, "product_create_request")
        response = requests.post(
            f"{SETTINGS.N8N_WEBHOOK_BASE_URL}{"-test" if SETTINGS.N8N_TEST == "TRUE" else ""}/{SETTINGS.N8N_WEBHOOK_PATH}", json={"xmlContent": xml_content})
        response.raise_for_status()
        result: dict = response.json()
        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# @router.post("/xml-parser", response_model=dict)
# async def parse_xml(request: Request):
#     try:
#         # XML 본문 읽기 (bytes)
#         body = await request.body()
#         # EUC-KR 디코딩 → UTF-8 로 변경
#         decoded = body.decode("euc-kr")
#         # XML → dict 변환
#         result = xmltodict.parse(decoded)
#         return {"status": "success", "result": result}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
