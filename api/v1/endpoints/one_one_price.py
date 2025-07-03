from fastapi import APIRouter, Depends
from schemas.one_one_price.request.one_one_price_request import OneOnePriceCreate
from schemas.one_one_price.response.one_one_price_response import OneOnePriceResponse
from core.db import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from services.usecase.product_one_one_price_usecase import ProductOneOnePriceUsecase


router = APIRouter(
    prefix="/one-one-price",
    tags=["one-one-price"],
)

def get_product_one_one_price_usecase(session: AsyncSession = Depends(get_async_session)) -> ProductOneOnePriceUsecase:
    return ProductOneOnePriceUsecase(session=session)

@router.post("", response_model=OneOnePriceResponse)
async def one_one_price_setting(
    request: OneOnePriceCreate = Depends(),
    product_one_one_price_usecase: ProductOneOnePriceUsecase = Depends(get_product_one_one_price_usecase)
):
    return OneOnePriceResponse.from_dto(await product_one_one_price_usecase.calculate_and_save_one_one_prices(
        product_nm=request.product_nm,
    ))