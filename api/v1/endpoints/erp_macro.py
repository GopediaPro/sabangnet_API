from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from utils.sabangnet_logger import get_logger
from minio_handler import upload_file_to_minio, get_minio_file_url, temp_file_to_object_name, delete_temp_file, url_arrange
from sqlalchemy.ext.asyncio import AsyncSession
from core.db import get_async_session
from services.order.macros.order_macro_service import run_macro
from datetime import datetime

logger = get_logger(__name__)

router = APIRouter(
    prefix="/erp-macro",
    tags=["erp-macro"],
)

@router.post("/excel-run-macro")
async def excel_run_macro(
    template_code: str = Form(...),
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_async_session)
):
    """
    프론트에서 template_code와 엑셀 파일을 받아 macro 실행 후 minio 활용 excel 파일 업로드.
    """
    try:
        # Excel file template_code 에 따라 실행
        logger.info(f"Excel file template_code 에 따라 실행")
        logger.info(f"file: {file}")
        file_name = file.filename
        logger.info(f"file_name: {file_name}")
        temp_upload_file_path = temp_file_to_object_name(file)
        file_path = await run_macro(session, template_code, temp_upload_file_path)
        delete_temp_file(temp_upload_file_path)
        logger.info(f"file_name 실행 후 파일 삭제")
        # minio 업로드
        date_now = datetime.now().strftime("%Y%m%d%H%M%S")
        minio_object_name = f"excel/{template_code}/{date_now}_{file_name}"
        object_name = upload_file_to_minio(file_path, minio_object_name)
        delete_temp_file(file_path)
        # minio 파일 위치 반환
        file_url = get_minio_file_url(object_name)
        return {"file_url": url_arrange(file_url), "object_name": minio_object_name, "template_code": template_code}
    except Exception as e:
        logger.error(f"excel_run_macro error: {e}")
        raise HTTPException(status_code=500, detail=str(e))