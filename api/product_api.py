from fastapi import APIRouter, HTTPException
from fastapi import Depends
from repository.product_repository import ProductRepository
from services.product_xml_parse import ProductXmlParser
from utils.convert_xlsx import ConvertXlsx
from pathlib import Path
from utils.product_create_field_mapping import PRODUCT_CREATE_FIELD_MAPPING
from core.db import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/api/product"
)


@router.get("/")
async def root():
    return {"message": "product api"}


@router.post("/xml/db/create")
async def root(xml_path: str, db: AsyncSession = Depends(get_async_session)):
    xml_parse = ProductXmlParser()
    crud = ProductRepository(db)
    # xml parse
    product_data: list[dict] = xml_parse.xml_parse(xml_path)
    # DB insert test_product_raw_data
    product_raw_id: list[int] = await crud.product_raw_data_create(product_data)

    return {"DB_insert_raw_id": product_raw_id}



