from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Query
from utils.logs.sabangnet_logger import get_logger
from minio_handler import upload_and_get_url_and_size, url_arrange
from sqlalchemy.ext.asyncio import AsyncSession
from core.db import get_async_session
from services.macro.order_macro_service import process_macro_with_tempfile, run_macro_with_db
from schemas.macros.response.excel_macro_response import ExcelRunMacroResponse
from schemas.macros.batch_process_dto import BatchProcessDto
from services.batch_info_service import BatchInfoService, build_and_save_batch
import json
from schemas.macros.response.excel_list_response import ExcelListResponse, ExcelItem
from schemas.macros.request.batch_process_request import BatchProcessRequest
from services.usecase.data_processing_usecase import DataProcessingUsecase

logger = get_logger(__name__)


router = APIRouter(
    prefix="/macro",
    tags=["macro"],
)


def get_batch_info_service(session: AsyncSession = Depends(get_async_session)) -> BatchInfoService:
    return BatchInfoService(session=session)


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
    session: AsyncSession = Depends(get_async_session)
):
    request_obj = BatchProcessRequest(**json.loads(request))
    logger.info(f"request_obj: {request_obj}")
    original_filename = file.filename
    try:
        template_code = request_obj.template_code
        logger.info(f"original_filename: {original_filename}")
        file_name, file_path = await process_macro_with_tempfile(session, template_code, file)
        file_url, minio_object_name, file_size = upload_and_get_url_and_size(
            file_path, template_code, file_name)
        file_url = url_arrange(file_url)
        batch_id = await build_and_save_batch(session, BatchProcessDto.build_success, original_filename, file_url, file_size, request_obj)
        return ExcelRunMacroResponse.build_success(
            template_code=template_code,
            batch_id=batch_id,
            file_url=file_url,
            object_name=minio_object_name
        )
    except Exception as e:
        logger.error(f"excel_run_macro error: {e}")
        batch_id = await build_and_save_batch(session, BatchProcessDto.build_error, original_filename, request_obj, str(e))
        return ExcelRunMacroResponse.build_error(
            template_code=template_code,
            batch_id=batch_id,
            message=str(e)
        )


@router.post("/db-run-macro")
async def db_run_macro(
    template_code: str = Form(...),
    session: AsyncSession = Depends(get_async_session)
):
    """
    프론트에서 template_code를 받아 macro 실행 후 성공한 레코드 수 반환.
    """
    try:
        saved_count = await run_macro_with_db(session, template_code)
        return {"saved_count": saved_count}
    except Exception as e:
        logger.error(f"db_run_macro error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get-batch-info-all")
async def get_batch_info_all(
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=1000),
    batch_info_service: BatchInfoService = Depends(get_batch_info_service),
):
    items, total = await batch_info_service.get_batch_info_paginated(page, page_size)
    dto_items = [BatchProcessDto.model_validate(item) for item in items]
    return ExcelListResponse[BatchProcessDto](
        total=total,
        page=page,
        page_size=page_size,
        items=[ExcelItem[BatchProcessDto](data=dto_items)]
    )


@router.get("/get-batch-info-latest")
async def get_batch_info_latest(
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=1000),
    batch_info_service: BatchInfoService = Depends(get_batch_info_service),
):
    items, total = await batch_info_service.get_batch_info_latest(page, page_size)
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
    successful_results, failed_results, total_saved_count = await data_processing_usecase.bulk_save_down_form_orders_from_macro_run_excel(files)
    return {
        "total_saved_count": total_saved_count,
        "successful_results": successful_results,
        "failed_results": failed_results
    }
