"""
Ecount ERP API v2
이카운트 ERP API v2 엔드포인트
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Body, Response
from typing import Optional, List, Dict, Any
import json

from utils.logs.sabangnet_logger import get_logger
from utils.decorators import api_exception_handler, validate_excel_file
from schemas.integration_request import IntegrationRequest, Metadata
from schemas.integration_response import ResponseHandler, Metadata as ResponseMetadata
from schemas.ecount.ecount_excel_sale_dto import EcountSaleExcelRequestDto
from services.ecount.ecount_auth_service import EcountAuthManager
from services.ecount.ecount_excel_sale_service import EcountExcelSaleService

logger = get_logger(__name__)

router = APIRouter(
    prefix="/ecount",
    tags=["ecount-v2"],
)

# 서비스 의존성
def get_auth_manager() -> EcountAuthManager:
    return EcountAuthManager()

def get_excel_sale_service() -> EcountExcelSaleService:
    return EcountExcelSaleService()

@router.post(
    "/sale/create-bulk-from-excel",
    summary="Excel 파일로부터 판매 데이터 일괄 생성",
    description="Excel 파일을 업로드하여 이카운트 판매 데이터를 일괄 생성합니다.",
    response_class=Response
)
@api_exception_handler(logger)
async def create_sale_bulk_from_excel(
    file: UploadFile = File(..., description="판매 데이터 Excel 파일"),
    request: str = Body(
        ...,
        examples=EcountSaleExcelRequestDto.model_config["json_schema_extra"]["examples"]
    ),
    auth_manager: EcountAuthManager = Depends(get_auth_manager),
    excel_sale_service: EcountExcelSaleService = Depends(get_excel_sale_service)
):
    """
    Excel 파일을 업로드하여 이카운트 판매 데이터를 일괄 생성합니다.
    """
    try:
        # JSON 문자열을 파싱하여 IntegrationRequest 객체 생성
        request_obj = IntegrationRequest[EcountSaleExcelRequestDto](**json.loads(request))
        
        # 파일 검증
        validate_excel_file(file)
        
        # 파일 내용 읽기
        content = await file.read()
        
        # 인증 정보 가져오기
        auth_info = await auth_manager.get_authenticated_info_from_env(request_obj.data.is_test)
        if not auth_info:
            return ResponseHandler.unauthorized(
                message="환경변수 인증 실패",
                metadata=ResponseMetadata(
                    version="v2",
                    request_id=request_obj.metadata.request_id
                )
            )
        
        # Excel 파일 업로드 및 판매 처리
        response_data = await excel_sale_service.process_excel_sale_upload(
            file_content=content,
            file_name=file.filename,
            sheet_name=request_obj.data.sheet_name,
            auth_info=auth_info,
            user_id=request_obj.metadata.request_id
        )
        
        # 표준화된 응답 생성
        metadata = ResponseMetadata(
            version="v2",
            request_id=request_obj.metadata.request_id
        )
        
        return ResponseHandler.ok(data=response_data, metadata=metadata)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Excel 업로드 처리 중 오류 발생: {e}")
        return ResponseHandler.internal_error(
            message=f"Excel 업로드 처리 중 오류가 발생했습니다: {str(e)}",
            metadata=ResponseMetadata(
                version="v2",
                request_id=request_obj.metadata.request_id if 'request_obj' in locals() else None
            )
        )

@router.get("/health")
@api_exception_handler(logger)
async def health_check():
    """
    헬스 체크 엔드포인트
    """
    return {
        "status": "healthy",
        "service": "ecount-erp-api-v2",
        "timestamp": "2024-12-25"
    }
