# std
from typing import Optional
# fastapi
from fastapi import APIRouter, Depends, Body
# sql
from core.db import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
# service
from services.hanjin.hanjin_print_service import HanjinPrintService
# utils
from utils.logs.sabangnet_logger import get_logger
from utils.decorators import hanjin_api_handler, validate_hanjin_env_vars
# schema
from schemas.integration_request import IntegrationRequest
from schemas.integration_response import ResponseHandler, Metadata
from schemas.hanjin.hanjin_printWbls_dto import (
    CreateAndProcessPrintwblsRequest,
    CreateAndProcessPrintwblsResponse,
)


logger = get_logger(__name__)


router = APIRouter(
    prefix="/hanjin",
    tags=["hanjin"],
)


def get_hanjin_print_service(session: AsyncSession = Depends(get_async_session)) -> HanjinPrintService:
    return HanjinPrintService(session=session)


@router.post("/create-and-process-printwbls-from-down-form-orders")
@hanjin_api_handler(error_code="CREATE_AND_PROCESS_PRINTWBLS_ERROR", error_message="down_form_orders에서 printwbls 생성 및 처리 중 오류가 발생했습니다.")
async def create_and_process_printwbls_from_down_form_orders(
    request: IntegrationRequest[CreateAndProcessPrintwblsRequest] = Body(...),
    _: bool = Depends(validate_hanjin_env_vars),
    print_service: HanjinPrintService = Depends(get_hanjin_print_service)
):
    """
    down_form_orders 테이블에서 gmarket_bundle, basic_bundle 데이터를 조회하여
    PrintWblsRequest를 생성하고 한진 API를 호출한 후,
    응답으로 hanjin_printwbls 테이블에 생성하고 down_form_orders 테이블에 invoice_no를 업데이트합니다.
    
    처리 과정:
    1. down_form_orders 테이블에서 form_name이 'gmarket_bundle', 'basic_bundle'이고 invoice_no가 없는 데이터 조회
       (order_date 범위 필터 적용)
    2. batch_process 생성 (request_id 기반)
    3. 각 레코드에 대해 msg_key 생성 (YYMMDD + random num(XX) + 요청개수순서)
    4. PrintWblsRequest 생성 (snd_zip은 "08609" 고정값 사용)
    5. 한진 API 호출 (csr_num은 환경변수 HANJIN_CSR_NUM 사용)
    6. API 응답으로 hanjin_printwbls 테이블에 새 레코드 생성
    7. down_form_orders 테이블의 해당 idx에 invoice_no, batch_id, process_dt 업데이트
    8. 생성된 데이터를 Excel 파일로 변환하여 MinIO에 업로드
    9. batch_process에 파일 정보 업데이트
    
    Args:
        request: IntegrationRequest<CreateAndProcessPrintwblsRequest>
            - data.limit: 처리할 최대 건수 (기본값: 100)
            - data.order_date_from: 주문 시작 날짜 (YYYY-MM-DD)
            - data.order_date_to: 주문 종료 날짜 (YYYY-MM-DD)
            - metadata.request_id: 요청 ID (batch_process 생성용)
        
    Returns:
        처리 결과 정보 (batch_id 포함)
    """
    try:
        # 요청 데이터 추출
        limit = request.data.limit or 100
        order_date_from = request.data.order_date_from
        order_date_to = request.data.order_date_to
        request_id = request.metadata.request_id if request.metadata else None
        
        # 서비스 호출
        response = await print_service.create_and_process_printwbls_from_down_form_orders(
            limit=limit,
            order_date_from=order_date_from,
            order_date_to=order_date_to,
            request_id=request_id
        )
        
        # 메타데이터 생성
        metadata = Metadata(
            version="2.0",
            request_id=request.metadata.request_id if request.metadata else None
        )
        
        logger.info("down_form_orders에서 printwbls 생성 및 처리 완료")
        
        # ResponseHandler를 사용하여 응답 생성
        return ResponseHandler.created(response, metadata)
        
    except Exception as e:
        logger.error(f"create_and_process_printwbls_from_down_form_orders 실패: {str(e)}")
        
        # 에러 메타데이터 생성
        metadata = Metadata(
            version="2.0",
            request_id=request.metadata.request_id if request.metadata else None
        )
        
        # ResponseHandler를 사용하여 에러 응답 생성
        return ResponseHandler.internal_error(
            message="down_form_orders에서 printwbls 생성 및 처리 중 오류가 발생했습니다.",
            metadata=metadata
        )
