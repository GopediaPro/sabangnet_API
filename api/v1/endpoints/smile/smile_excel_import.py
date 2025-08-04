"""
Smile Excel Import API
스마일배송 Excel 파일을 데이터베이스에 가져오는 API 엔드포인트
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any, Tuple
import time

from core.db import get_async_session
from services.smile.smile_excel_import_service import SmileExcelImportService
from utils.logs.sabangnet_logger import get_logger
from utils.decorators import smile_excel_import_handler, validate_excel_file
from schemas.smile.smile_excel_import_dto import (
    SmileErpDataImportResponseDto,
    SmileSettlementDataImportResponseDto,
    SmileSkuDataImportResponseDto,
    SmileAllDataImportResponseDto
)

logger = get_logger(__name__)

router = APIRouter(
    prefix="/smile-excel-import",
    tags=["smile-excel-import"]
)


async def get_smile_service(session: AsyncSession = Depends(get_async_session)) -> SmileExcelImportService:
    """스마일배송 서비스 의존성 주입"""
    return SmileExcelImportService(session)


@router.get("/", summary="스마일배송 Excel 가져오기 API 상태 확인")
async def get_api_status():
    """API 상태를 확인합니다."""
    return {"message": "Smile Excel Import API is running", "status": "ok"}


@router.post(
    "/erp-data",
    summary="ERP 데이터 Excel 가져오기",
    description="Excel 파일을 업로드하여 SmileErpData 테이블에 저장합니다.",
    response_model=SmileErpDataImportResponseDto
)
@smile_excel_import_handler()
async def import_erp_data_from_excel(
    file: UploadFile = File(..., description="ERP 데이터 Excel 파일"),
    sheet_name: str = Query("Sheet1", description="처리할 시트명"),
    clear_existing: bool = Query(False, description="기존 데이터 삭제 여부"),
    service: SmileExcelImportService = Depends(get_smile_service)
):
    """ERP 데이터 Excel 파일을 처리하여 데이터베이스에 저장합니다."""
    
    # 파일 검증
    validate_excel_file(file)
    
    # 파일 내용 읽기
    content = await file.read()
    
    # 서비스 호출
    return await service.import_erp_data(content, file.filename, sheet_name, clear_existing)


@router.post(
    "/settlement-data",
    summary="정산 데이터 Excel 가져오기",
    description="Excel 파일을 업로드하여 SmileSettlementData 테이블에 저장합니다.",
    response_model=SmileSettlementDataImportResponseDto
)
@smile_excel_import_handler()
async def import_settlement_data_from_excel(
    file: UploadFile = File(..., description="정산 데이터 Excel 파일"),
    site: str = Query(..., description="사이트명 (G마켓, 옥션)"),
    sheet_name: str = Query("Sheet1", description="처리할 시트명"),
    clear_existing: bool = Query(False, description="기존 데이터 삭제 여부"),
    service: SmileExcelImportService = Depends(get_smile_service)
):
    """정산 데이터 Excel 파일을 처리하여 데이터베이스에 저장합니다."""
    
    # site 파라미터 로깅 추가
    logger = get_logger(__name__)
    logger.info(f"정산 데이터 가져오기 요청 - site: '{site}' (type: {type(site)})")
    
    # 파일 검증
    validate_excel_file(file)
    
    # 파일 내용 읽기
    content = await file.read()
    
    # 서비스 호출
    return await service.import_settlement_data(content, file.filename, site, sheet_name, clear_existing)


@router.post(
    "/sku-data",
    summary="SKU 데이터 Excel 가져오기",
    description="Excel 파일을 업로드하여 SmileSkuData 테이블에 저장합니다.",
    response_model=SmileSkuDataImportResponseDto
)
@smile_excel_import_handler()
async def import_sku_data_from_excel(
    file: UploadFile = File(..., description="SKU 데이터 Excel 파일"),
    sheet_name: str = Query("Sheet1", description="처리할 시트명"),
    clear_existing: bool = Query(False, description="기존 데이터 삭제 여부"),
    service: SmileExcelImportService = Depends(get_smile_service)
):
    """SKU 데이터 Excel 파일을 처리하여 데이터베이스에 저장합니다."""
    
    # 파일 검증
    validate_excel_file(file)
    
    # 파일 내용 읽기
    content = await file.read()
    
    # 서비스 호출
    return await service.import_sku_data(content, file.filename, sheet_name, clear_existing)


@router.post(
    "/all-data",
    summary="모든 스마일배송 데이터 Excel 가져오기",
    description="여러 Excel 파일을 업로드하여 모든 스마일배송 테이블에 저장합니다.",
    response_model=SmileAllDataImportResponseDto
)
@smile_excel_import_handler()
async def import_all_smile_data_from_excel(
    erp_file: Optional[UploadFile] = File(None, description="ERP 데이터 Excel 파일"),
    settlement_file: Optional[UploadFile] = File(None, description="정산 데이터 Excel 파일"),
    sku_file: Optional[UploadFile] = File(None, description="SKU 데이터 Excel 파일"),
    clear_existing: bool = Query(False, description="기존 데이터 삭제 여부"),
    service: SmileExcelImportService = Depends(get_smile_service)
):
    """모든 스마일배송 데이터 Excel 파일을 처리하여 데이터베이스에 저장합니다."""
    
    # 파일 검증 및 수집
    files = {}
    
    if erp_file:
        validate_excel_file(erp_file)
        files["erp"] = (await erp_file.read(), erp_file.filename)
    
    if settlement_file:
        validate_excel_file(settlement_file)
        files["settlement"] = (await settlement_file.read(), settlement_file.filename)
    
    if sku_file:
        validate_excel_file(sku_file)
        files["sku"] = (await sku_file.read(), sku_file.filename)
    
    # 서비스 호출
    return await service.import_all_data(files, clear_existing)

