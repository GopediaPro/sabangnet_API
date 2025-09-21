# std
import tempfile
import os
from typing import Optional

# core
from core.db import get_async_session

# sql
from sqlalchemy.ext.asyncio import AsyncSession

# fastapi
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse

# service
from services.product_registration.product_integrated_service_v2 import ProductCodeIntegratedServiceV2

# schema
from schemas.integration_request import IntegrationRequest
from schemas.integration_response import ResponseHandler, Metadata
from schemas.product_registration.request.product_workflow_request import CompleteWorkflowRequest
from schemas.product_registration.response.product_workflow_response import CompleteWorkflowResponse

# utils
from utils.logs.sabangnet_logger import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/product",
    tags=["product-v2"],
)


# Dependency
def get_product_integrated_service_v2(
    session: AsyncSession = Depends(get_async_session),
) -> ProductCodeIntegratedServiceV2:
    return ProductCodeIntegratedServiceV2()


@router.post("/complete-workflow", response_class=JSONResponse)
async def process_complete_product_registration_workflow_v2(
    request: str = Form(..., description="요청 데이터 (JSON 문자열)"),
    file: UploadFile = File(..., description="Excel 파일"),
):
    """
    전체 상품 등록 워크플로우 V2를 처리합니다:
    1. Excel 파일 처리 및 DB 저장
    2. DB Transfer (product_registration_raw_data → test_product_raw_data) - bulk_result 기반
    3. DB to SabangAPI 요청 - transfer_result 기반
    -- Examples:
    {"data": { "sheet_name": "상품등록" }, "metadata": { "request_id": "lyckabc" }}
    """
    try:
        import json
        request_obj = IntegrationRequest[CompleteWorkflowRequest](**json.loads(request))
        
        sheet_name = request_obj.data.sheet_name
        request_id = request_obj.metadata.request_id
        
        logger.info(
            f"[process_complete_product_registration_workflow_v2] 시작 - 파일: {file.filename}, "
            f"요청자: {request_id}, 시트명: {sheet_name}"
        )

        # 파일 확장자 검증
        if not file.filename.endswith(('.xlsx', '.xls')):
            return ResponseHandler.bad_request(
                message="Excel 파일(.xlsx, .xls)만 업로드 가능합니다.",
                metadata=Metadata(version="v2", request_id=request_id),
            )
        
        # 임시 파일로 저장
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # 서비스 인스턴스 생성
            service = ProductCodeIntegratedServiceV2()
            
            logger.info(f"전체 상품 등록 워크플로우 V2 시작: {file.filename}")
            
            # 워크플로우 실행
            result = await service.process_complete_product_registration_workflow_v2(
                file_path=temp_file_path,
                sheet_name=sheet_name
            )
            
            logger.info(f"전체 상품 등록 워크플로우 V2 완료: {result.get('success', False)}")
            
            return ResponseHandler.ok(
                data=CompleteWorkflowResponse(**result),
                metadata=Metadata(version="v2", request_id=request_id),
            )
            
        finally:
            # 임시 파일 삭제
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except Exception as e:
        logger.error(f"[process_complete_product_registration_workflow_v2] 오류: {str(e)}", exc_info=True)
        return ResponseHandler.internal_error(
            message=f"워크플로우 V2 처리 중 오류 발생: {str(e)}",
            metadata=Metadata(version="v2", request_id=request_id if 'request_id' in locals() else None),
        )
