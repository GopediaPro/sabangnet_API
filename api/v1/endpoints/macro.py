from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Query, Body
from utils.sabangnet_logger import get_logger
from minio_handler import upload_and_get_url_and_size, url_arrange
from sqlalchemy.ext.asyncio import AsyncSession
from core.db import get_async_session
from services.order.macros.order_macro_service import process_macro_with_tempfile, run_macro_with_db
from schemas.order.data_processing import ProcessDataRequest
from schemas.batch_process_dto import BatchProcessDto
from services.batch_info_service import build_and_save_batch
from schemas.order.response.order_response import ExcelRunMacroResponse
from services.batch_info_service import BatchInfoService
import json

logger = get_logger(__name__)

router = APIRouter(
    prefix="/macro",
    tags=["macro"],
)

def get_batch_info_service(session: AsyncSession = Depends(get_async_session)) -> BatchInfoService:
    return BatchInfoService(session=session)

@router.post("/excel-run-macro")
async def excel_run_macro(
    request: str = Form(
        ...,
        description=json.dumps(ProcessDataRequest.Config.json_schema_extra['example'], indent=2)
    ),
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_async_session)
    ):
    request_obj = ProcessDataRequest(**json.loads(request))
    logger.info(f"request_obj: {request_obj}")
    original_filename = file.filename
    try:
        template_code = request_obj.template_code
        logger.info(f"original_filename: {original_filename}")
        file_name, file_path = await process_macro_with_tempfile(session, template_code, file)
        file_url, minio_object_name, file_size = upload_and_get_url_and_size(file_path, template_code, file_name)
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

