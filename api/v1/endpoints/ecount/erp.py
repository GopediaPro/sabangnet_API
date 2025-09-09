"""
이카운트 ERP API 엔드포인트
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from core.db import get_async_session
from utils.logs.sabangnet_logger import get_logger
from typing import Optional
from utils.decorators import api_exception_handler

# 스키마 임포트
from schemas.ecount.auth_schemas import (
    ZoneRequest, ZoneResponse, LoginRequest, LoginResponse, EcountAuthInfo
)
from schemas.ecount.ecount_schemas import (
    EcountSaleDto, EcountSaleRequest, EcountSaleResponse,
    EcountBatchProcessRequest, EcountBatchProcessResponse,
    EcountApiResponse
)

# 서비스 임포트
from services.ecount.ecount_auth_service import EcountAuthService, EcountAuthManager
from services.ecount.ecount_sale_service import EcountSaleService
from services.ecount.ecount_batch_integration_service import EcountBatchIntegrationService


logger = get_logger(__name__)


router = APIRouter(
    prefix="/ecount",
    tags=["ecount"],
)


# 서비스 의존성
def get_auth_service() -> EcountAuthService:
    return EcountAuthService()


def get_auth_manager() -> EcountAuthManager:
    return EcountAuthManager()


def get_sale_service() -> EcountSaleService:
    return EcountSaleService()

def get_batch_integration_service() -> EcountBatchIntegrationService:
    return EcountBatchIntegrationService()


@router.post("/zone", response_model=ZoneResponse)
@api_exception_handler(logger)
async def get_zone_info(
    zone_request: ZoneRequest,
    is_test: bool = Query(True, description="테스트 환경 여부"),
    auth_service: EcountAuthService = Depends(get_auth_service)
):
    """
    Zone 정보를 조회합니다.
    """
    zone_response = await auth_service.get_zone_info(zone_request.COM_CODE, is_test)
    if not zone_response:
        raise HTTPException(status_code=400, detail="Zone 정보 조회 실패")
    return zone_response


@router.post("/login", response_model=LoginResponse)
@api_exception_handler(logger)
async def login(
    login_request: LoginRequest,
    is_test: bool = Query(True, description="테스트 환경 여부"),
    auth_service: EcountAuthService = Depends(get_auth_service)
):
    """
    이카운트 로그인을 수행합니다.
    """
    auth_info = EcountAuthInfo(
        com_code=login_request.COM_CODE,
        user_id=login_request.USER_ID,
        api_cert_key=login_request.API_CERT_KEY,
        zone=login_request.ZONE,
        domain=""
    )
    login_response = await auth_service.login(auth_info, is_test)
    if not login_response:
        raise HTTPException(status_code=400, detail="로그인 실패")
    return login_response

@router.post("/authenticate")
@api_exception_handler(logger)
async def authenticate(
    is_test: bool = Query(True, description="테스트 환경 여부"),
    auth_service: EcountAuthService = Depends(get_auth_service)
):
    """
    환경변수를 사용하여 자동 인증을 수행합니다.
    """
    session_id, auth_info = await auth_service.authenticate_with_env(is_test)
    if not session_id or not auth_info:
        raise HTTPException(status_code=400, detail="환경변수 인증 실패")
    return {
        "session_id": session_id,
        "auth_info": auth_info.model_dump(),
        "message": "환경변수 인증 성공"
    }


@router.post("/sale/create", response_model=EcountSaleResponse)
@api_exception_handler(logger)
async def create_sale(
    sale_request: EcountSaleRequest,
    is_test: bool = Query(True, description="테스트 환경 여부"),
    auth_manager: EcountAuthManager = Depends(get_auth_manager),
    sale_service: EcountSaleService = Depends(get_sale_service)
):
    """
    환경변수를 사용하여 판매를 생성합니다.
    """
    auth_info = await auth_manager.get_authenticated_info_from_env(is_test)
    if not auth_info:
        raise HTTPException(status_code=401, detail="환경변수 인증 실패")
    
    results = []
    errors = []
    
    for sale_data in sale_request.sales:
        logger.info(f"sale_data: {sale_data}")
        sale_response, validation_errors = await sale_service.create_sale_with_validation(sale_data, auth_info, is_test)
        if validation_errors:
            errors.extend(validation_errors)
        if sale_response:
            results.append(sale_data)
    
    return EcountSaleResponse(
        success=len(results) > 0,
        message=f"{len(results)}건 성공, {len(errors)}건 실패",
        data=results,
        errors=errors
    )


@router.post("/sale/create-bulk", response_model=EcountSaleResponse)
@api_exception_handler(logger)
async def create_sale_bulk(
    sale_request: EcountSaleRequest,
    is_test: bool = Query(True, description="테스트 환경 여부"),
    auth_manager: EcountAuthManager = Depends(get_auth_manager),
    sale_service: EcountSaleService = Depends(get_sale_service)
):
    """
    여러 판매를 일괄 생성합니다.
    """
    auth_info = await auth_manager.get_authenticated_info_from_env(is_test)
    if not auth_info:
        raise HTTPException(status_code=401, detail="환경변수 인증 실패")
    
    # create_sales_with_validation을 사용하여 배치 처리
    api_response, errors = await sale_service.create_sales_with_validation(
        sale_dtos=sale_request.sales,
        auth_info=auth_info
    )
    
    # 성공한 데이터만 필터링
    successful_sales = [
        sale for sale in sale_request.sales 
        if sale.is_success
    ]
    
    # 응답 메시지 구성
    success_count = api_response.Data.SuccessCnt if api_response and api_response.Data else 0
    fail_count = api_response.Data.FailCnt if api_response and api_response.Data else 0
    
    message = f"배치 처리 완료: {success_count}건 성공, {fail_count}건 실패"
    if errors:
        message += f", {len(errors)}건 검증 오류"
    
    return EcountSaleResponse(
        success=success_count > 0,
        message=message,
        data=successful_sales,
        errors=errors,
        api_response=api_response.Data if api_response else None
    )


@router.post("/sale/validate")
@api_exception_handler(logger)
async def validate_sale_data(
    sale_data: EcountSaleDto,
    sale_service: EcountSaleService = Depends(get_sale_service)
):
    """
    판매 데이터를 검증합니다.
    """
    errors = sale_service.validate_sale_data(sale_data)
    return {
        "is_valid": len(errors) == 0,
        "errors": errors,
        "data": sale_data.model_dump()
    }

@router.post("/sale/create-from-orders-by-condition", response_model=EcountBatchProcessResponse)
@api_exception_handler(logger)
async def create_sales_from_orders_by_condition(
    request: EcountBatchProcessRequest,
    is_test: bool = Query(True, description="테스트 환경 여부"),
    auth_manager: EcountAuthManager = Depends(get_auth_manager),
    batch_service: EcountBatchIntegrationService = Depends(get_batch_integration_service)
):
    """
    환경변수를 사용하여 조건에 따라 주문을 조회하고 이카운트로 판매를 생성합니다.
    """
    auth_info = await auth_manager.get_authenticated_info_from_env(is_test)
    if not auth_info:
        raise HTTPException(status_code=401, detail="환경변수 인증 실패")
    
    # batch_service에 auth_info 전달 (필요한 경우)
    result = await batch_service.process_orders_by_condition(request)
    return result


@router.post("/sale/calculate-amounts")
@api_exception_handler(logger)
async def calculate_amounts(
    qty: float,
    price: float,
    vat_rate: float = 0.1,
    sale_service: EcountSaleService = Depends(get_sale_service)
):
    """
    수량과 단가로 공급가액과 부가세를 계산합니다.
    """
    from decimal import Decimal
    supply_amt, vat_amt = sale_service.calculate_amounts(
        Decimal(str(qty)), 
        Decimal(str(price)), 
        Decimal(str(vat_rate))
    )
    return {
        "qty": qty,
        "price": price,
        "vat_rate": vat_rate,
        "supply_amt": float(supply_amt),
        "vat_amt": float(vat_amt),
        "total_amt": float(supply_amt + vat_amt)
    }

@router.delete("/auth/clear-cache")
@api_exception_handler(logger)
async def clear_auth_cache(
    com_code: Optional[str] = None,
    user_id: Optional[str] = None,
    is_test: Optional[bool] = None,
    auth_manager: EcountAuthManager = Depends(get_auth_manager)
):
    """
    인증 캐시를 클리어합니다.
    """
    auth_manager.clear_cache(com_code, user_id, is_test)
    return {
        "message": "캐시가 클리어되었습니다.",
        "cleared_for": {
            "com_code": com_code,
            "user_id": user_id,
            "is_test": is_test
        }
    }


@router.get("/health")
@api_exception_handler(logger)
async def health_check():
    """
    헬스 체크 엔드포인트
    """
    return {
        "status": "healthy",
        "service": "ecount-erp-api",
        "timestamp": "2024-12-25"
    }

