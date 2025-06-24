from fastapi import APIRouter, HTTPException
from fastapi import Depends
from repository.product_repository import ProductRepository
from services.product_xml_parse import ProductXmlParser
from core.db import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from services.product_create_origin import ProductCreateService
from repository.product_repository import ProductRepository

router = APIRouter(
    prefix="/api/product"
)


@router.get("/")
async def root():
    return {"message": "product api"}


@router.post("/xml/db/create")
async def root(xml_path: str, db: AsyncSession = Depends(get_async_session)) -> dict:
    """
    xml_path: xml file path
    db: database session
    """
    xml_parse = ProductXmlParser()
    crud = ProductRepository(db)
    # xml parse
    product_data: list[dict] = xml_parse.xml_parse(xml_path)
    # DB insert test_product_raw_data
    product_raw_id: list[int] = await crud.product_raw_data_create(product_data)

    return {"DB_insert_raw_id": product_raw_id}


@router.post("/xml/db/prop1_cd/update")
async def root(product_raw_id:int, prop1_cd: int = None, db: AsyncSession = Depends(get_async_session)) -> dict:
    """
    prop1_cd: prop1_cd value
    db: database session
    """
    crud = ProductRepository(db)
    xml = ProductCreateService()
    # prop1_cd update
    peoduct_dict = await crud.prodout_prop1_cd_update(product_raw_id, prop1_cd)
    # xml create
    product_xml = xml.create_request_xml(product_data=peoduct_dict)
    return {"product_xml": product_xml}

