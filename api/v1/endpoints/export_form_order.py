from fastapi import APIRouter, Depends, Query, Body, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from core.db import get_async_session
from services.order.export_form_order_service import ExportFormOrderService
from utils.response_status import RowStatus
from utils.sabangnet_logger import get_logger
from schemas.order.export_form_order_dto import ExportFormOrderDto
from schemas.order.request.down_form_order_request import DownFormOrderCreate, DownFormOrderUpdate, DownFormOrderDelete
from schemas.order.response.down_form_order_response import DownFormOrderListResponse, DownFormOrderBulkResponse, DownFormOrderItem
from services.order.export_form_order_service import ExportFormOrderService
from utils.excel_handler import ExcelHandler
from minio_handler import upload_and_get_url, temp_file_to_object_name
from services.order.data_processing_pipeline import DataProcessingPipeline

logger = get_logger(__name__)

router = APIRouter(
    prefix="/export-form-orders",
    tags=["export-form-orders"],
)

def get_export_form_order_service(session: AsyncSession = Depends(get_async_session)) -> ExportFormOrderService:
    return ExportFormOrderService(session=session)

@router.get("", response_model=DownFormOrderListResponse)
async def list_export_form_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=1000),
    template_code: Optional[str] = Query(
        None,
        description="form_name 필터링: 'all'은 전체, ''(빈값)은 form_name이 NULL 또는 빈 값, 그 외는 해당 값과 일치하는 항목 조회"
    ),
    export_form_order_service: ExportFormOrderService = Depends(get_export_form_order_service),
):
    items, total = await export_form_order_service.get_export_form_orders_paginated(page, page_size, template_code)
    dto_items = [ExportFormOrderDto.model_validate(item) for item in items]
    return DownFormOrderListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[{
            "data": [dto.model_dump() for dto in dto_items],
            "status": None,
            "message": None
        }]
    )

@router.post("/bulk", response_model=DownFormOrderBulkResponse)
async def bulk_create_down_form_orders(
    request: DownFormOrderCreate,
    export_form_order_service: ExportFormOrderService = Depends(get_export_form_order_service),
):
    logger.info(f"[bulk_create] 요청: {request}")
    try:
        result = await export_form_order_service.bulk_create_export_form_orders(request.items)
        logger.info(f"[bulk_create] 성공: {len(request.items)}건 생성")
        return DownFormOrderBulkResponse(results=[
            DownFormOrderItem(
                data=[item],
                status=RowStatus.SUCCESS,
                message=None
            ) for item in request.items
        ])
    except Exception as e:
        logger.error(f"[bulk_create] 실패: {str(e)}", e)
        raise

@router.put("/bulk", response_model=DownFormOrderBulkResponse)
async def bulk_update_down_form_orders(
    request: DownFormOrderUpdate,
    export_form_order_service: ExportFormOrderService = Depends(get_export_form_order_service),
):
    logger.info(f"[bulk_update] 요청: {request}")
    try:
        result = await export_form_order_service.bulk_update_export_form_orders(request.items)
        logger.info(f"[bulk_update] 성공: {len(request.items)}건 수정")
        return DownFormOrderBulkResponse(results=[
            DownFormOrderItem(
                data=[item],
                status=RowStatus.SUCCESS,
                message=None
            ) for item in request.items
        ])
    except Exception as e:
        logger.error(f"[bulk_update] 실패: {str(e)}", e)
        raise

@router.delete("/bulk", response_model=DownFormOrderBulkResponse)
async def bulk_delete_down_form_orders(
    request: DownFormOrderDelete = Body(...),
    export_form_order_service: ExportFormOrderService = Depends(get_export_form_order_service),
):
    logger.info(f"[bulk_delete] 요청: {request}")
    try:
        result = await export_form_order_service.bulk_delete_export_form_orders(request.ids)
        logger.info(f"[bulk_delete] 성공: {len(request.ids)}건 삭제")
        return DownFormOrderBulkResponse(results=[
            DownFormOrderItem(
                data=[],
                status=RowStatus.SUCCESS,
                message=None
            ) for id in request.ids
        ])
    except Exception as e:
        logger.error(f"[bulk_delete] 실패: {str(e)}", e)
        raise

@router.delete("/delete-all")
async def delete_all_down_form_orders(
    export_form_order_service: ExportFormOrderService = Depends(get_export_form_order_service),
):
    try:
        await export_form_order_service.delete_all_export_form_orders()
        return {"message": "모든 데이터 삭제 완료"}
    except Exception as e:
        logger.error(f"[delete_all] 실패: {str(e)}", e)
        raise

@router.delete("/delete-duplicate")
async def delete_duplicate_down_form_orders(
    export_form_order_service: ExportFormOrderService = Depends(get_export_form_order_service),
):
    deleted_count = await export_form_order_service.delete_duplicate_export_form_orders()
    return {"message": f"중복 데이터 삭제 완료: {deleted_count}개 행 삭제됨"}

@router.post("/get-macro-finish-excel-upload-to-url")
async def get_macro_finish_excel_upload_to_url(
    template_code: str = Form(...),
    file: UploadFile = File(...)
):
    """
    프론트에서 template_code와 macro가 완료된 엑셀 파일을 받아 MinIO에 업로드하고 presigned URL을 반환합니다.
    """
    file_name = file.filename
    file_path = temp_file_to_object_name(file)
    file_url, minio_object_name = upload_and_get_url(file_path, template_code, file_name)
    return {"file_url": file_url, "object_name": minio_object_name, "template_code": template_code}


@router.post("/get-macro-finish-excel-to-db")
async def get_macro_finish_excel_to_db(
    template_code: str = Form(...),
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_async_session)
):
    """
    프론트에서 template_code와 macro가 완료된엑셀 파일을 받아 DB에 저장
    """
    pipeline = DataProcessingPipeline(session)
    dataframe = ExcelHandler.from_upload_file_to_dataframe(file)
    saved_count = await pipeline.process_excel_to_down_form_orders(dataframe, template_code)
    return {"saved_count": saved_count}
