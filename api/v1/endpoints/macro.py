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


@router.post("/excel-run-macro")
async def excel_run_macro(
    request: BatchProcessRequest = Body(...),
    file: UploadFile = File(...),
    data_processing_usecase: DataProcessingUsecase = Depends(get_data_processing_usecase),
    batch_info_create_service: BatchInfoCreateService = Depends(get_batch_info_create_service)
    ):
    original_filename = file.filename
    try:
        template_code = request.template_code
        logger.info(f"original_filename: {original_filename}")
        file_name, file_path = await data_processing_usecase.process_macro_with_tempfile(template_code, file)
        file_url, minio_object_name, file_size = upload_and_get_url_and_size(file_path, template_code, file_name)
        file_url = url_arrange(file_url)
        batch_id = await batch_info_create_service.build_and_save_batch(
            BatchProcessDto.build_success,
            original_filename,
            file_url,
            file_size,
            request
        )
        return ExcelRunMacroResponse.build_success(
            template_code=template_code,
            batch_id=batch_id,
            file_url=file_url,
            object_name=minio_object_name
        )
    except Exception as e:
        logger.error(f"excel_run_macro error: {e}")
        batch_id = await batch_info_create_service.build_and_save_batch(
            BatchProcessDto.build_error,
            original_filename,
            request,
            str(e)
        )
        return ExcelRunMacroResponse.build_error(
            template_code=template_code,
            batch_id=batch_id,
            message=str(e)
        )


@router.post("/db-run-macro")
async def db_run_macro(
    template_code: str = Form(...),
    data_processing_usecase: DataProcessingUsecase = Depends(get_data_processing_usecase),
    batch_info_create_service: BatchInfoCreateService = Depends(get_batch_info_create_service)
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
    batch_info_read_service: BatchInfoReadService = Depends(get_batch_info_read_service),
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
    batch_info_read_service: BatchInfoReadService = Depends(get_batch_info_read_service),
):
    items, total = await batch_info_read_service.get_batch_info_latest(page, page_size)
    dto_items = [BatchProcessDto.model_validate(item) for item in items]
    return ExcelListResponse[BatchProcessDto](
        total=total,
        page=page,
        page_size=page_size,
        items=[ExcelItem[BatchProcessDto](data=dto_items)]
    )