from fastapi import APIRouter, Depends, Body, Query
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from utils.logs.sabangnet_logger import get_logger
from utils.decorators import hanjin_api_handler, validate_hanjin_env_vars
from schemas.hanjin.hanjin_auth_schemas import HmacResponse
from schemas.hanjin.hanjin_printWbls_dto import PrintWblsResponse, PrintWblsRequest, CreatePrintwblsFromDownFormOrdersResponse, ProcessPrintwblsWithApiResponse
from services.hanjin.hanjin_auth_service import HanjinAuthService
from services.hanjin.hanjin_print_service import HanjinPrintService
from core.db import get_async_session

logger = get_logger(__name__)

router = APIRouter(
    prefix="/hanjin",
    tags=["hanjin"],
)



# 서비스 의존성
def get_hanjin_auth_service() -> HanjinAuthService:
    return HanjinAuthService()


def get_hanjin_print_service(session: AsyncSession = Depends(get_async_session)) -> HanjinPrintService:
    return HanjinPrintService(session=session)


@router.post("/hmac-generate-test", response_model=HmacResponse)
@hanjin_api_handler()
async def hmac_generate_test(
    _: bool = Depends(validate_hanjin_env_vars),
    auth_service: HanjinAuthService = Depends(get_hanjin_auth_service)
):
    """
    한진 API의 /v1/util/hmacgen 엔드포인트에 직접 요청하여 Authorization을 받아옵니다.
    
    환경변수에서 HANJIN_API(x-api-key)와 HANJIN_CLIENT_ID(client_id)를 가져와서
    한진 API에 POST 요청을 보내고 받은 Authorization을 반환합니다.
    """
    response = await auth_service.generate_hmac_with_env_vars_from_api()
    logger.info("한진 API로부터 HMAC 인증 생성 성공")
    return response


@router.post("/print-wbls-manual", response_model=PrintWblsResponse)
@hanjin_api_handler(error_code="PRINT_WBLS_ERROR", error_message="운송장 출력 요청 중 오류가 발생했습니다.")
async def print_wbls(
    print_request: PrintWblsRequest,
    idx: Optional[str] = Query(None, description="주문번호 (선택사항)"),
    _: bool = Depends(validate_hanjin_env_vars),
    print_service: HanjinPrintService = Depends(get_hanjin_print_service)
):
    """
    한진 API의 print-wbls 엔드포인트에 직접 요청하여 운송장 분류정보를 받아옵니다.
    
    환경변수에서 HANJIN_API(x-api-key), HANJIN_CLIENT_ID(client_id), HANJIN_CSR_NUM(csr_num)를 가져와서
    한진 API에 POST 요청을 보내고 받은 운송장 분류정보를 반환합니다.
    
    최대 요청 건수는 100건입니다.
    응답 결과는 데이터베이스에 자동으로 저장됩니다.
    """
    response = await print_service.generate_print_wbls_with_env_vars_from_api_and_save(print_request, idx)
    logger.info("한진 API로부터 운송장 분류정보 생성 및 데이터베이스 저장 성공")
    return response

@router.post("/create-printwbls-from-down-form-orders", response_model=CreatePrintwblsFromDownFormOrdersResponse)
@hanjin_api_handler(error_code="CREATE_PRINTWBLS_ERROR", error_message="down_form_orders에서 hanjin_printwbls 생성 중 오류가 발생했습니다.")
async def create_printwbls_from_down_form_orders(
    limit: Optional[int] = Query(100, description="처리할 최대 건수 (기본값: 100)"),
    _: bool = Depends(validate_hanjin_env_vars),
    print_service: HanjinPrintService = Depends(get_hanjin_print_service)
):
    """
    down_form_orders 테이블에서 invoice_no가 없는 데이터를 조회하여
    hanjin_printwbls 테이블에 입력합니다.
    
    매핑 관계:
    - idx = idx (주문번호)
    - receive_addr = prt_add (배송지 주소)
    - receive_zipcode = zip_cod (우편번호)
    
    Args:
        limit: 처리할 최대 건수 (기본값: 100)
        
    Returns:
        처리 결과 정보
    """
    response = await print_service.create_hanjin_printwbls_from_down_form_orders(limit)
    logger.info("down_form_orders에서 hanjin_printwbls 생성 완료")
    return response


@router.post("/process-printwbls-from-db", response_model=ProcessPrintwblsWithApiResponse)
@hanjin_api_handler(error_code="PROCESS_PRINTWBLS_ERROR", error_message="hanjin_printwbls API 처리 중 오류가 발생했습니다.")
async def process_printwbls_from_db(
    limit: Optional[int] = Query(100, description="처리할 최대 건수 (기본값: 100)"),
    _: bool = Depends(validate_hanjin_env_vars),
    print_service: HanjinPrintService = Depends(get_hanjin_print_service)
):
    """
    hanjin_printwbls 테이블의 데이터를 기반으로 한진 API를 호출하고 응답을 업데이트합니다.
    
    처리 과정:
    1. hanjin_printwbls 테이블에서 prt_add, snd_zip, zip_cod가 있는 레코드 조회
    2. 각 레코드에 대해 msg_key 생성 (YYMMDD + random num(XX) + 요청개수순서)
    3. 한진 API 호출 (csr_num은 환경변수 HANJIN_CSR_NUM 사용)
    4. API 응답으로 레코드 업데이트
    
    Args:
        limit: 처리할 최대 건수 (기본값: 100)
        
    Returns:
        처리 결과 정보
    """
    response = await print_service.process_hanjin_printwbls_from_db(limit)
    logger.info("hanjin_printwbls API 처리 완료")
    return response



