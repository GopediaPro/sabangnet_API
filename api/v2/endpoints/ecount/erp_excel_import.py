"""
Ecount Excel Import API
이카운트 Excel 파일을 데이터베이스에 가져오는 API 엔드포인트
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Query, Response, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any, Tuple
import time
import os
import json

from core.db import get_async_session
from services.ecount.ecount_excel_import_service import EcountExcelImportService
from utils.logs.sabangnet_logger import get_logger
from utils.decorators import validate_excel_file, ecount_excel_import_handler
from schemas.ecount.ecount_excel_import_dto import (
    EcountErpPartnerCodeImportResponseDto,
    EcountIyesCostImportResponseDto,
    EcountAllDataImportResponseDto,
    EcountExcelDownloadResponseDto,
    EcountExcelImportRequestDto,
    EcountAllDataImportRequestDto
)
from schemas.integration_request import IntegrationRequest, Metadata
from schemas.integration_response import ResponseHandler, Metadata as ResponseMetadata

logger = get_logger(__name__)


def get_examples_from_dto(dto_class):
    """DTO 클래스에서 예시를 가져오는 헬퍼 함수"""
    return dto_class.model_config.get("json_schema_extra", {}).get("examples", [])

router = APIRouter(
    prefix="/ecount-excel-import",
    tags=["ecount-excel-import"]
)


async def get_ecount_service(session: AsyncSession = Depends(get_async_session)) -> EcountExcelImportService:
    """이카운트 서비스 의존성 주입"""
    return EcountExcelImportService(session)


@router.get("/", summary="이카운트 Excel 가져오기 API 상태 확인")
async def get_api_status():
    """API 상태를 확인합니다."""
    return {"message": "Ecount Excel Import API is running", "status": "ok"}


@router.post(
    "/erp-partner-code",
    summary="ERP 파트너 코드 데이터 Excel 가져오기",
    description="Excel 파일을 업로드하여 EcountErpPartnerCode 테이블에 저장합니다.",
    response_class=Response
)
@ecount_excel_import_handler()
async def import_erp_partner_code_from_excel(
    file: UploadFile = File(..., description="ERP 파트너 코드 데이터 Excel 파일"),
    request: str = Body(
        ...,
        examples=get_examples_from_dto(EcountExcelImportRequestDto)
    ),
    service: EcountExcelImportService = Depends(get_ecount_service)
):
    """ERP 파트너 코드 데이터 Excel 파일을 처리하여 데이터베이스에 저장합니다."""
    
    # JSON 문자열을 파싱하여 IntegrationRequest 객체 생성
    request_obj = IntegrationRequest[EcountExcelImportRequestDto](**json.loads(request))
    
    # 파일 검증
    validate_excel_file(file)
    
    # 파일 내용 읽기
    content = await file.read()
    
    # 서비스 호출
    result = await service.import_erp_partner_code_data(
        content, 
        file.filename, 
        request_obj.data.sheet_name, 
        request_obj.data.clear_existing
    )
    
    # 표준화된 응답 생성
    metadata = ResponseMetadata(
        version="v2",
        request_id=request_obj.metadata.request_id
    )
    
    return ResponseHandler.ok(data=result, metadata=metadata)


@router.post(
    "/iyes-cost",
    summary="IYES 단가 데이터 Excel 가져오기",
    description="Excel 파일을 업로드하여 EcountIyesCost 테이블에 저장합니다.",
    response_class=Response
)
@ecount_excel_import_handler()
async def import_iyes_cost_from_excel(
    file: UploadFile = File(..., description="IYES 단가 데이터 Excel 파일"),
    request: str = Body(
        ...,
        examples=get_examples_from_dto(EcountExcelImportRequestDto)
    ),
    service: EcountExcelImportService = Depends(get_ecount_service)
):
    """IYES 단가 데이터 Excel 파일을 처리하여 데이터베이스에 저장합니다."""
    
    # JSON 문자열을 파싱하여 IntegrationRequest 객체 생성
    request_obj = IntegrationRequest[EcountExcelImportRequestDto](**json.loads(request))
    
    # 파일 검증
    validate_excel_file(file)
    
    # 파일 내용 읽기
    content = await file.read()
    
    # 서비스 호출
    result = await service.import_iyes_cost_data(
        content, 
        file.filename, 
        request_obj.data.sheet_name, 
        request_obj.data.clear_existing
    )
    
    # 표준화된 응답 생성
    metadata = ResponseMetadata(
        version="v2",
        request_id=request_obj.metadata.request_id
    )
    
    return ResponseHandler.ok(data=result, metadata=metadata)


@router.post(
    "/all-data",
    summary="모든 이카운트 데이터 Excel 가져오기",
    description="하나의 Excel 파일에서 여러 시트를 읽어 모든 이카운트 테이블에 저장합니다.",
    response_class=Response
)
@ecount_excel_import_handler()
async def import_all_ecount_data_from_excel(
    file: UploadFile = File(..., description="이카운트 데이터 Excel 파일 (여러 시트 포함)"),
    request: str = Body(
        ...,
        examples=get_examples_from_dto(EcountAllDataImportRequestDto)
    ),
    service: EcountExcelImportService = Depends(get_ecount_service)
):
    """모든 이카운트 데이터 Excel 파일을 처리하여 데이터베이스에 저장합니다."""
    
    # JSON 문자열을 파싱하여 IntegrationRequest 객체 생성
    request_obj = IntegrationRequest[EcountAllDataImportRequestDto](**json.loads(request))
    
    # 파일 검증
    validate_excel_file(file)
    
    # 파일 내용 읽기
    content = await file.read()
    
    # 서비스 호출
    result = await service.import_all_data_from_single_file(
        content, 
        file.filename, 
        request_obj.data.erp_partner_code_sheet,
        request_obj.data.iyes_cost_sheet,
        request_obj.data.clear_existing
    )
    
    # 표준화된 응답 생성
    metadata = ResponseMetadata(
        version="v2",
        request_id=request_obj.metadata.request_id
    )
    
    return ResponseHandler.ok(data=result, metadata=metadata)


@router.post(
    "/download/erp-partner-code",
    summary="ERP 파트너 코드 데이터 Excel 다운로드",
    description="ERP 파트너 코드 데이터를 Excel 파일로 다운로드합니다.",
    response_class=Response
)
@ecount_excel_import_handler()
async def download_erp_partner_code_excel(
    request: str = Body(
        ...,
        examples=[
            {
                "data": {},
                "metadata": {
                    "request_id": "req_12345"
                }
            }
        ]
    ),
    service: EcountExcelImportService = Depends(get_ecount_service)
):
    """ERP 파트너 코드 데이터를 Excel 파일로 다운로드합니다."""
    
    # JSON 문자열을 파싱하여 IntegrationRequest 객체 생성
    request_obj = IntegrationRequest[dict](**json.loads(request))
    
    # 서비스 호출
    result = await service.download_erp_partner_code_excel()
    
    # 표준화된 응답 생성
    metadata = ResponseMetadata(
        version="v2",
        request_id=request_obj.metadata.request_id
    )
    
    return ResponseHandler.ok(data=result, metadata=metadata)


@router.post(
    "/download/iyes-cost",
    summary="IYES 단가 데이터 Excel 다운로드",
    description="IYES 단가 데이터를 Excel 파일로 다운로드합니다.",
    response_class=Response
)
@ecount_excel_import_handler()
async def download_iyes_cost_excel(
    request: str = Body(
        ...,
        examples=[
            {
                "data": {},
                "metadata": {
                    "request_id": "req_12345"
                }
            }
        ]
    ),
    service: EcountExcelImportService = Depends(get_ecount_service)
):
    """IYES 단가 데이터를 Excel 파일로 다운로드합니다."""
    
    # JSON 문자열을 파싱하여 IntegrationRequest 객체 생성
    request_obj = IntegrationRequest[dict](**json.loads(request))
    
    # 서비스 호출
    result = await service.download_iyes_cost_excel()
    
    # 표준화된 응답 생성
    metadata = ResponseMetadata(
        version="v2",
        request_id=request_obj.metadata.request_id
    )
    
    return ResponseHandler.ok(data=result, metadata=metadata)
