from core.db import get_async_session
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession
from utils.logs.sabangnet_logger import get_logger
from fastapi import APIRouter, Depends, HTTPException
from services.usecase.product_one_one_price_usecase import ProductOneOnePriceUsecase
from schemas.one_one_price.request.one_one_price_request import OneOnePriceCreate, OneOnePriceBulkCreate
from schemas.one_one_price.response.one_one_price_response import OneOnePriceResponse, OneOnePriceBulkResponse


logger = get_logger(__name__)


router = APIRouter(
    prefix="/one-one-price",
    tags=["one-one-price"],
)


def get_product_one_one_price_usecase(session: AsyncSession = Depends(get_async_session)) -> ProductOneOnePriceUsecase:
    return ProductOneOnePriceUsecase(session=session)


@router.post("/", response_model=OneOnePriceResponse)
async def one_one_price_setting(
    request: OneOnePriceCreate = Depends(),
    product_one_one_price_usecase: ProductOneOnePriceUsecase = Depends(get_product_one_one_price_usecase)
) -> OneOnePriceResponse:
    try:
        return OneOnePriceResponse.from_dto(await product_one_one_price_usecase.calculate_and_save_one_one_price(
            product_nm=request.product_nm,
            gubun=request.gubun,
        ))
    except DBAPIError as e:
        if "integer out of range" in str(e):
            raise HTTPException(status_code=400, detail="원본 상품 가격이 너무 커서 계산할 수 없습니다.")
        else:
            raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/bulk", response_model=OneOnePriceBulkResponse)
async def one_one_price_bulk_setting(
    request: OneOnePriceBulkCreate,
    product_one_one_price_usecase: ProductOneOnePriceUsecase = Depends(get_product_one_one_price_usecase)
) -> OneOnePriceBulkResponse:
    # JSON 데이터를 DTO로 변환
    product_nm_and_gubun_list = request.to_dto()
    try:
        return OneOnePriceBulkResponse.from_dto(await product_one_one_price_usecase.calculate_and_save_one_one_prices_bulk(
            product_nm_and_gubun_list=product_nm_and_gubun_list,
        ))
    except DBAPIError as e:
        if "integer out of range" in str(e):
            raise HTTPException(status_code=400, detail="원본 상품 가격이 너무 커서 계산할 수 없습니다.")
        else:
            raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))