from fastapi import APIRouter, Depends, Query, Body, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from core.db import get_async_session
from services.order.down_form_order_read_service import DownFormOrderReadService
from services.order.down_form_order_create_service import DownFormOrderCreateService
from schemas.order.request.down_form_order_request import DownFormOrderCreate, DownFormOrderUpdate, DownFormOrderDelete
from schemas.order.response.down_form_order_response import DownFormOrderListResponse, DownFormOrderBulkResponse, DownFormOrderItem
from schemas.order.down_form_order_dto import DownFormOrderDto
from utils.response_status import make_row_result, RowStatus
from utils.sabangnet_logger import get_logger
from minio_handler import upload_and_get_url, temp_file_to_object_name
from services.order.data_processing_pipeline import DataProcessingPipeline

logger = get_logger(__name__)

router = APIRouter(
    prefix="/down-form-orders",
    tags=["down-form-orders"],
)

def get_down_form_order_create_service(session: AsyncSession = Depends(get_async_session)) -> DownFormOrderCreateService:
    return DownFormOrderCreateService(session=session)

def get_down_form_order_read_service(session: AsyncSession = Depends(get_async_session)) -> DownFormOrderReadService:
    return DownFormOrderReadService(session=session)

@router.get("", response_model=DownFormOrderListResponse)
async def list_down_form_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=1000),
    template_code: Optional[str] = Query(
        None,
        description="form_name 필터링: 'all'은 전체, ''(빈값)은 form_name이 NULL 또는 빈 값, 그 외는 해당 값과 일치하는 항목 조회"
    ),
    down_form_order_read_service: DownFormOrderReadService = Depends(get_down_form_order_read_service),
):
    items, total = await down_form_order_read_service.get_down_form_orders_paginated(page, page_size, template_code)
    dto_items = [DownFormOrderDto.model_validate(item) for item in items]
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
    down_form_order_create_service: DownFormOrderCreateService = Depends(get_down_form_order_create_service),
):
    logger.info(f"[bulk_create] 요청: {request}")
    try:
        result = await down_form_order_create_service.bulk_create_down_form_orders(request.items)
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
    down_form_order_create_service: DownFormOrderCreateService = Depends(get_down_form_order_create_service),
):
    logger.info(f"[bulk_update] 요청: {request}")
    try:
        result = await down_form_order_create_service.bulk_update_down_form_orders(request.items)
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
    down_form_order_create_service: DownFormOrderCreateService = Depends(get_down_form_order_create_service),
):
    logger.info(f"[bulk_delete] 요청: {request}")
    try:
        result = await down_form_order_create_service.bulk_delete_down_form_orders(request.ids)
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

@router.post("/upload-excel-file")
async def upload_excel_file(
    template_code: str = Form(...),
    file: UploadFile = File(...)
):
    """
    프론트에서 template_code와 엑셀 파일을 받아 MinIO에 업로드하고 presigned URL을 반환합니다.
    """
    file_name = file.filename
    file_path = temp_file_to_object_name(file)
    file_url, minio_object_name = upload_and_get_url(file_path, template_code, file_name)
    return {"file_url": file_url, "object_name": minio_object_name, "template_code": template_code}


@router.post("/get-excel-to-db")
async def get_excel_to_db(
    template_code: str = Form(...),
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_async_session)
):
    """
    프론트에서 template_code와 엑셀 파일을 받아 DB에 저장
    """
    pipeline = DataProcessingPipeline(session)
    saved_count = await pipeline.process_excel_to_down_form_orders(file, template_code)
    return {"saved_count": saved_count}