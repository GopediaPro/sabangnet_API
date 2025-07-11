from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from utils.sabangnet_logger import get_logger
from minio_handler import upload_and_get_url, url_arrange
from sqlalchemy.ext.asyncio import AsyncSession
from core.db import get_async_session
from services.order.macros.order_macro_service import process_macro_with_tempfile

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
        file_name, file_path = await process_macro_with_tempfile(session, template_code, file)
        # minio 업로드
        file_url, minio_object_name = upload_and_get_url(file_path, template_code, file_name)
        return {"file_url": url_arrange(file_url), "object_name": minio_object_name, "template_code": template_code}
    except Exception as e:
        logger.error(f"excel_run_macro error: {e}")
        raise HTTPException(status_code=500, detail=str(e))