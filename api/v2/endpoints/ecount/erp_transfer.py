"""
ERP Transfer API
ERP 데이터 전송을 위한 API 엔드포인트
"""

from fastapi import APIRouter, Depends, Response, Body
from sqlalchemy.ext.asyncio import AsyncSession
import json

from core.db import get_async_session
from services.ecount.erp_transfer_service import ErpTransferService
from schemas.ecount.erp_transfer_dto import ErpTransferRequestDto, ErpTransferResponseDto
from schemas.integration_request import IntegrationRequest, Metadata
from schemas.integration_response import ResponseHandler, Metadata as ResponseMetadata
from utils.logs.sabangnet_logger import get_logger


def get_examples_from_dto(dto_class):
    """DTO 클래스에서 예시를 가져오는 헬퍼 함수"""
    return dto_class.model_config.get("json_schema_extra", {}).get("examples", [])

logger = get_logger(__name__)

router = APIRouter(
    prefix="/ecount/erp-transfer",
    tags=["ecount-erp-transfer"]
)


async def get_erp_transfer_service(session: AsyncSession = Depends(get_async_session)) -> ErpTransferService:
    """ERP 전송 서비스 의존성 주입"""
    return ErpTransferService(session)


@router.get("/", summary="ERP 전송 API 상태 확인")
async def get_api_status():
    """API 상태를 확인합니다."""
    return {"message": "ERP Transfer API is running", "status": "ok"}


@router.post(
    "/download",
    summary="ERP 데이터 Excel 다운로드",
    description="down_form_orders 테이블의 데이터를 ERP 업로드용 Excel 파일로 다운로드합니다.",
    response_class=Response
)
async def download_erp_data(
    request: IntegrationRequest[ErpTransferRequestDto] = Body(
        ...,
        description="ERP 전송 요청 데이터",
        examples=get_examples_from_dto(IntegrationRequest[ErpTransferRequestDto])
    ),
    service: ErpTransferService = Depends(get_erp_transfer_service)
):
    """
    ERP 데이터를 Excel 파일로 다운로드합니다.
    
    Form Name별 처리 규칙:
    - okmart_erp_sale_ok: "erp"가 포함되고 "fld_dsp"에 "아이예스"가 포함되지 않은 데이터
    - okmart_erp_sale_iyes: "erp"가 포함되고 "fld_dsp"에 "아이예스"가 포함된 데이터
    - iyes_erp_sale_iyes: "erp"가 포함되고 "fld_dsp"에 "아이예스"가 포함된 데이터
    - iyes_erp_purchase_iyes: "erp"가 포함되고 "fld_dsp"에 "아이예스"가 포함된 데이터 (구매용)
    """
    
    try:
        # 서비스 호출
        result = await service.process_erp_transfer(request.data)
        
        # 표준화된 응답 생성
        metadata = ResponseMetadata(
            version="v2",
            request_id=request.metadata.request_id
        )
        
        logger.info(f"ERP transfer completed successfully. Batch ID: {result.batch_id}")
        
        return ResponseHandler.ok(data=result, metadata=metadata)
        
    except Exception as e:
        logger.error(f"ERP transfer failed: {str(e)}")
        
        # 에러 응답 생성
        metadata = ResponseMetadata(
            version="v2",
            request_id=getattr(request.metadata, 'request_id', None) if 'request' in locals() else None
        )
        
        return ResponseHandler.internal_error(
            message=f"ERP transfer failed: {str(e)}",
            metadata=metadata
        )
