# std
from typing import Optional
# core
from core.db import get_async_session
# sql
from sqlalchemy.ext.asyncio import AsyncSession
# fastapi
from fastapi import APIRouter, Depends, Query, Body, UploadFile, File, Form
# service
from services.usecase.data_processing_usecase import DataProcessingUsecase
from services.down_form_orders.export_form_order_read_service import ExportFormOrderReadService
from services.down_form_orders.export_form_order_update_service import ExportFormOrderUpdateService
from services.down_form_orders.export_form_order_delete_service import ExportFormOrderDeleteService
from services.down_form_orders.export_form_order_create_service import ExportFormOrderCreateService
# schema
from schemas.down_form_orders.export_form_order_dto import ExportFormOrderDto
from schemas.down_form_orders.response.export_form_orders_response import (
    ExportFormOrderResponse,
    ExportFormOrderBulkResponse,
    ExportFormOrderPaginationResponse,
)
from schemas.down_form_orders.request.export_form_orders_request import (
    ExportFormOrderBulkCreateJsonRequest,
    ExportFormOrderBulkUpdateJsonRequest,
    ExportFormOrderBulkDeleteJsonRequest
)
# utils
from utils.response_status import RowStatus
from utils.logs.sabangnet_logger import get_logger
# excel
from utils.excels.excel_handler import ExcelHandler
# minio
from minio_handler import upload_and_get_url, temp_file_to_object_name


logger = get_logger(__name__)


router = APIRouter(
    prefix="/export-form-order",
    tags=["export-form-order"],
)


def get_export_form_order_create_service(session: AsyncSession = Depends(get_async_session)) -> ExportFormOrderCreateService:
    return ExportFormOrderCreateService(session=session)


def get_export_form_order_update_service(session: AsyncSession = Depends(get_async_session)) -> ExportFormOrderUpdateService:
    return ExportFormOrderUpdateService(session=session)


def get_export_form_order_delete_service(session: AsyncSession = Depends(get_async_session)) -> ExportFormOrderDeleteService:
    return ExportFormOrderDeleteService(session=session)


def get_data_processing_usecase(session: AsyncSession = Depends(get_async_session)) -> DataProcessingUsecase:
    return DataProcessingUsecase(session=session)


def get_export_form_order_read_service(session: AsyncSession = Depends(get_async_session)) -> ExportFormOrderReadService:
    return ExportFormOrderReadService(session=session)


@router.get("", response_model=ExportFormOrderBulkResponse)
async def export_form_orders(
    skip: int = Query(0, ge=0, description="건너뛸 건수"),
    limit: int = Query(200, ge=1, le=200, description="조회할 건수"),
    export_form_order_read_service: ExportFormOrderReadService = Depends(get_export_form_order_read_service),
):
    export_form_orders: list[ExportFormOrderDto] = await export_form_order_read_service.get_export_form_orders(skip=skip, limit=limit)
    response = ExportFormOrderBulkResponse(
        items=[]
    )
    logger.info(f"[export_form_orders] 요청: {skip}, {limit}")
    for export_form_order in export_form_orders:
        try:
            response.items.append(
                ExportFormOrderResponse(
                    item=ExportFormOrderDto.model_validate(export_form_order),
                    status=RowStatus.SUCCESS,
                    message="success"
                )
            )
        except Exception as e:
            response.items.append(
                ExportFormOrderResponse(
                    item=None,
                    status=RowStatus.ERROR,
                    message=str(e)
                )
            )
    return response


@router.get("/pagination", response_model=ExportFormOrderPaginationResponse)
async def export_form_orders_pagination(
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=1000),
    template_code: Optional[str] = Query(
        None,
        description="form_name 필터링: 'all'은 전체, ''(빈값)은 form_name이 NULL 또는 빈 값, 그 외는 해당 값과 일치하는 항목 조회"
    ),
    export_form_order_read_service: ExportFormOrderReadService = Depends(get_export_form_order_read_service),
):
    items, total = await export_form_order_read_service.get_export_form_orders_paginated(page, page_size, template_code)
    dto_items = [ExportFormOrderDto.model_validate(item) for item in items]
    return ExportFormOrderPaginationResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[
            ExportFormOrderResponse(
                item=dto,
                status=RowStatus.SUCCESS,
                message="success"
            ) for dto in dto_items
        ]
    )


@router.post("/bulk", response_model=ExportFormOrderBulkResponse)
async def bulk_create_export_form_orders(
    request: ExportFormOrderBulkCreateJsonRequest,
    export_form_order_create_service: ExportFormOrderCreateService = Depends(get_export_form_order_create_service),
):
    logger.info(f"[bulk_create] 요청: {request}")
    try:
        result = await export_form_order_create_service.bulk_create_export_form_orders(request.items)
        logger.info(f"[bulk_create] 성공: {len(request.items)}건 생성")
        return ExportFormOrderBulkResponse(items=[
            ExportFormOrderResponse(
                item=ExportFormOrderDto.model_validate(item),
                status=RowStatus.SUCCESS,
                message="success"
            ) for item in request.items
        ])
    except Exception as e:
        logger.error(f"[bulk_create] 실패: {str(e)}", e)
        raise


@router.put("/bulk", response_model=ExportFormOrderBulkResponse)
async def bulk_update_export_form_orders(
    request: ExportFormOrderBulkUpdateJsonRequest,
    export_form_order_update_service: ExportFormOrderUpdateService = Depends(get_export_form_order_update_service),
):
    logger.info(f"[bulk_update] 요청: {request}")
    try:
        result = await export_form_order_update_service.bulk_update_export_form_orders(request.items)
        logger.info(f"[bulk_update] 성공: {len(request.items)}건 수정")
        return ExportFormOrderBulkResponse(items=[
            ExportFormOrderResponse(
                item=ExportFormOrderDto.model_validate(item),
                status=RowStatus.SUCCESS,
                message="success"
            ) for item in request.items
        ])
    except Exception as e:
        logger.error(f"[bulk_update] 실패: {str(e)}", e)
        raise


@router.delete("/bulk", response_model=ExportFormOrderBulkResponse)
async def bulk_delete_export_form_orders(
    request: ExportFormOrderBulkDeleteJsonRequest = Body(...),
    export_form_order_delete_service: ExportFormOrderDeleteService = Depends(get_export_form_order_delete_service),
):
    logger.info(f"[bulk_delete] 요청: {request}")
    try:
        result = await export_form_order_delete_service.bulk_delete_export_form_orders(request.ids)
        logger.info(f"[bulk_delete] 성공: {len(request.ids)}건 삭제")
        return ExportFormOrderBulkResponse(items=[
            ExportFormOrderResponse(
                item=None,
                status=RowStatus.SUCCESS,
                message="success"
            ) for order_id in request.ids
        ])
    except Exception as e:
        logger.error(f"[bulk_delete] 실패: {str(e)}", e)
        raise


@router.delete("/all")
async def delete_all_export_form_orders(
    export_form_order_delete_service: ExportFormOrderDeleteService = Depends(get_export_form_order_delete_service),
):
    try:
        await export_form_order_delete_service.delete_all_export_form_orders()
        return {"message": "모든 데이터 삭제 완료"}
    except Exception as e:
        logger.error(f"[delete_all] 실패: {str(e)}", e)
        raise


@router.delete("/duplicate")
async def delete_duplicate_export_form_orders(
    export_form_order_delete_service: ExportFormOrderDeleteService = Depends(get_export_form_order_delete_service),
):
    deleted_count = await export_form_order_delete_service.delete_duplicate_export_form_orders()
    return {"message": f"중복 데이터 삭제 완료: {deleted_count}개 행 삭제됨"}


@router.post("/excel-to-minio/finished-macro")
async def upload_macro_finish_excel_file_and_get_url(
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


@router.post("/excel-to-db/finished-macro")
async def get_macro_finish_excel_to_db(
    template_code: str = Form(...),
    file: UploadFile = File(...),
    data_processing_usecase: DataProcessingUsecase = Depends(get_data_processing_usecase)
):
    """
    프론트에서 template_code와 macro가 완료된엑셀 파일을 받아 DB에 저장
    """
    dataframe = ExcelHandler.from_upload_file_to_dataframe(file)
    saved_count = await data_processing_usecase.process_excel_to_down_form_orders(dataframe, template_code)
    return {"saved_count": saved_count}
