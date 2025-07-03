from fastapi import APIRouter, Depends
from schemas.mall_price.request.create_mall_price_form import CreateMallPriceForm
from schemas.mall_price.response.setting_mall_price_respones import SettingMallPriceResponse
from core.db import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from services.usecase.product_mall_price_usecase import ProductMallPriceUsecase


router = APIRouter(
    prefix="/mall-price",
    tags=["mall-price"],
)

def get_product_mall_price_usecase(session: AsyncSession = Depends(get_async_session)) -> ProductMallPriceUsecase:
    return ProductMallPriceUsecase(session=session)

@router.post("", response_model=SettingMallPriceResponse)
async def mall_price_setting(
    request: CreateMallPriceForm = Depends(),
    product_mall_price_usecase: ProductMallPriceUsecase = Depends(get_product_mall_price_usecase)
):
    return SettingMallPriceResponse.from_dto(await product_mall_price_usecase.setting_mall_price(
        product_nm=request.product_nm,
    ))