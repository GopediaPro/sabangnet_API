from core.db import get_async_session
from fastapi import APIRouter, Depends, HTTPException
from schemas.mall_price.request.create_mall_price_form import CreateMallPriceForm
from schemas.mall_price.response.setting_price_response import SettingPriceResponse
from sqlalchemy.ext.asyncio import AsyncSession
from services.usecase.product_mall_price_usecase import ProductMallPriceUsecase
from utils.logs.sabangnet_logger import get_logger
from sqlalchemy.exc import DBAPIError


logger = get_logger(__name__)


router = APIRouter(
    prefix="/mall-price",
    tags=["mall-price"],
)

def get_product_mall_price_usecase(session: AsyncSession = Depends(get_async_session)) -> ProductMallPriceUsecase:
    return ProductMallPriceUsecase(session=session)

@router.post("", response_model=SettingPriceResponse)
async def mall_price_setting(
    request: CreateMallPriceForm = Depends(),
    product_mall_price_usecase: ProductMallPriceUsecase = Depends(get_product_mall_price_usecase)
):
    try:
        result = await product_mall_price_usecase.setting_mall_price(
            compayny_goods_cd=request.compayny_goods_cd,
        )
        return SettingPriceResponse(**result)
    except DBAPIError as e:
        if "value out of int32 range" in str(e):
            raise HTTPException(status_code=400, detail="원본 상품 가격이 너무 커서 계산할 수 없습니다.")
        else:
            raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))