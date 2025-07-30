from core.db import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from utils.logs.sabangnet_logger import get_logger
from minio_handler import upload_and_get_url_and_size, url_arrange
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Query, Body

from services.usecase.data_processing_usecase import DataProcessingUsecase
from services.macro_batch_processing.batch_info_read_service import BatchInfoReadService
from services.macro_batch_processing.batch_info_create_service import BatchInfoCreateService

from schemas.macro_batch_processing.batch_process_dto import BatchProcessDto
from schemas.macro_batch_processing.request.batch_process_request import BatchProcessRequest
from schemas.macro_batch_processing.response.excel_macro_response import ExcelRunMacroResponse
from schemas.macro_batch_processing.response.excel_list_response import ExcelListResponse, ExcelItem
from schemas.macros.response.run_macro_response import BulkRunMacroResponse
import json

logger = get_logger(__name__)


router = APIRouter(
    prefix="/macro",
    tags=["macro"],
)


def get_data_processing_usecase(session: AsyncSession = Depends(get_async_session)) -> DataProcessingUsecase:
    return DataProcessingUsecase(session=session)


def get_batch_info_create_service(session: AsyncSession = Depends(get_async_session)) -> BatchInfoCreateService:
    return BatchInfoCreateService(session=session)


def get_batch_info_read_service(session: AsyncSession = Depends(get_async_session)) -> BatchInfoReadService:
    return BatchInfoReadService(session=session)


def get_data_processing_usecase(session: AsyncSession = Depends(get_async_session)) -> DataProcessingUsecase:
    return DataProcessingUsecase(session=session)


@router.post("/excel-run-macro")
async def excel_run_macro(
    request: str = Form(
        ...,
        description=json.dumps(
            BatchProcessRequest.Config.json_schema_extra['example'], indent=2)
    ),
    file: UploadFile = File(...),
    data_processing_usecase: DataProcessingUsecase = Depends(
        get_data_processing_usecase)
):
    """
    엑셀 파일을 업로드하여 매크로를 실행하고 MinIO URL을 반환합니다.
    """
    request_obj = BatchProcessRequest(**json.loads(request))

    result = await data_processing_usecase.get_excel_run_macro_minio_url(file, request_obj)

    if result.get("success"):
        return ExcelRunMacroResponse.build_success(
            template_code=result.get("template_code"),
            batch_id=result.get("batch_id"),
            file_url=result.get("file_url"),
            object_name=result.get("minio_object_name")
        )
    else:
        return ExcelRunMacroResponse.build_error(
            template_code=result.get("template_code"),
            batch_id=result.get("batch_id"),
            message=result.get("error_message")  # 에러 메시지
        )


@router.post("/excel-run-macro-bulk")
async def excel_run_macro_bulk(
    request: str = Form(
        ...,
        description=json.dumps(
            BatchProcessRequest.Config.json_schema_extra['example'], indent=2)
    ),
    files: list[UploadFile] = File(...),
    data_processing_usecase: DataProcessingUsecase = Depends(
        get_data_processing_usecase)
):
    request_obj = BatchProcessRequest(**json.loads(request))

    successful_results, failed_results, total_saved_count = (
        await data_processing_usecase.bulk_get_excel_run_macro_minio_url_and_save_db(files, request_obj))

    return BulkRunMacroResponse.build_total(
        total_saved_count=total_saved_count,
        successful_results=successful_results,
        failed_results=failed_results
    )


@router.post("/db-run-macro")
async def db_run_macro(
    template_code: str = Form(...),
    data_processing_usecase: DataProcessingUsecase = Depends(
        get_data_processing_usecase)
):
    """
    프론트에서 template_code를 받아 macro 실행 후 성공한 레코드 수 반환.
    """
    try:
        saved_count = await data_processing_usecase.run_macro_with_db(template_code)
        return {"saved_count": saved_count}
    except Exception as e:
        logger.error(f"db_run_macro error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/batch-info/all")
async def get_batch_info_all(
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1),
    batch_info_read_service: BatchInfoReadService = Depends(
        get_batch_info_read_service),
):
    items, total = await batch_info_read_service.get_batch_info_paginated(page, page_size)
    dto_items = [BatchProcessDto.model_validate(item) for item in items]
    return ExcelListResponse[BatchProcessDto](
        total=total,
        page=page,
        page_size=page_size,
        items=[ExcelItem[BatchProcessDto](data=dto_items)]
    )


@router.get("/batch-info/latest")
async def get_batch_info_latest(
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=1000),
    batch_info_read_service: BatchInfoReadService = Depends(
        get_batch_info_read_service),
):
    items, total = await batch_info_read_service.get_batch_info_latest(page, page_size)
    dto_items = [BatchProcessDto.model_validate(item) for item in items]
    return ExcelListResponse[BatchProcessDto](
        total=total,
        page=page,
        page_size=page_size,
        items=[ExcelItem[BatchProcessDto](data=dto_items)]
    )


@router.post("/excel-run-macro-db")
async def upload_excel_file_to_macro_get_url(
    file: UploadFile = File(...),
    data_processing_usecase: DataProcessingUsecase = Depends(
        get_data_processing_usecase)
):
    """
    프론트에서 엑셀 파일을 받아 파일 이름에서 template_code를 조회하여 매크로 실행 후 down_form_orders 테이블에 저장.
    """
    saved_count = await data_processing_usecase.save_down_form_orders_from_macro_run_excel(file, work_status="macro_run")
    return {"saved_count": saved_count}


@router.post("/excel-run-macro-db-bulk")
async def upload_excel_file_to_macro_get_url(
    files: list[UploadFile] = File(...),
    data_processing_usecase: DataProcessingUsecase = Depends(
        get_data_processing_usecase)
):
    """
    프론트에서 여러 개의 엑셀 파일을 받아 파일 이름에서 template_code를 조회하여 매크로 실행 후 down_form_orders 테이블에 저장.
    """
    successful_results, failed_results, total_saved_count = (
        await data_processing_usecase.bulk_save_down_form_orders_from_macro_run_excel(files)
    )
    return BulkRunMacroResponse.build_total(
        total_saved_count=total_saved_count,
        successful_results=successful_results,
        failed_results=failed_results
    )
