from core.db import get_async_session
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from schemas.mall_price.request.create_product_mall_value_form import CreateProductMallValueForm
from schemas.mall_price.response.setting_product_mall_value_response import SettingProductMallValueResponse
from schemas.integration_response import ResponseHandler, Metadata
from sqlalchemy.ext.asyncio import AsyncSession
from services.usecase.product_mall_value_usecase import ProductMallValueUsecase
from utils.logs.sabangnet_logger import get_logger
from sqlalchemy.exc import DBAPIError
from datetime import datetime, timezone


logger = get_logger(__name__)


router = APIRouter(
    prefix="/product-mall-value",
    tags=["product-mall-value"],
)

def get_product_mall_value_usecase(session: AsyncSession = Depends(get_async_session)) -> ProductMallValueUsecase:
    return ProductMallValueUsecase(session=session)

@router.post("", response_class=JSONResponse)
async def product_mall_value_setting(
    request: CreateProductMallValueForm = Depends(),
    product_mall_value_usecase: ProductMallValueUsecase = Depends(get_product_mall_value_usecase)
):
    """ProductMallValue 설정 API"""
    # 요청 데이터를 딕셔너리로 변환
    request_data = request.data.model_dump(exclude_unset=True)
    compayny_goods_cd = request_data.pop('compayny_goods_cd')
    request_id = request.metadata.request_id
    gubun = request_data.pop('gubun')
    standard_price = request_data.pop('standard_price', None)  # standard_price가 있으면 가져오고, 없으면 None
    
    try:
        
        result = await product_mall_value_usecase.setting_product_mall_value(
            compayny_goods_cd=compayny_goods_cd,
            gubun=gubun,
            request_id=request_id,
            standard_price=standard_price,  # standard_price 전달 (None일 수 있음)
            **request_data
        )
        
        # 응답 데이터 생성
        response_data = SettingProductMallValueResponse(**result)
        
        # 메타데이터 생성 (요청에서 받은 request_id 사용)
        metadata = Metadata(
            version="v2",
            request_id=request_id or f"product_mall_value_{datetime.now(timezone.utc).isoformat()}"
        )
        
        return ResponseHandler.created(data=response_data, metadata=metadata)
        
    except DBAPIError as e:
        if "value out of int32 range" in str(e):
            error_message = "원본 상품 가격이 너무 커서 계산할 수 없습니다."
        else:
            error_message = str(e)
        
        metadata = Metadata(
            version="v2",
            request_id=request_id or f"product_mall_value_error_{datetime.now(timezone.utc).isoformat()}"
        )
        
        return ResponseHandler.bad_request(
            message=error_message,
            metadata=metadata
        )
        
    except Exception as e:
        logger.error(f"ProductMallValue 설정 중 오류: {e}")
        
        metadata = Metadata(
            version="v2",
            request_id=request_id or f"product_mall_value_error_{datetime.now(timezone.utc).isoformat()}"
        )
        
        return ResponseHandler.internal_error(
            message=str(e),
            metadata=metadata
        )
