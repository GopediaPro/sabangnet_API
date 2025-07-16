# std
from typing import Optional, Any
# core
from core.db import get_async_session
# sql
from sqlalchemy.ext.asyncio import AsyncSession
# fastapi
from fastapi import APIRouter, Depends, Query, Body, UploadFile, File, Form
# service
from services.usecase.data_processing_usecase import DataProcessingUsecase
from services.usecase.down_form_order_template_usecase import DownFormOrderTemplateUsecase
from services.down_form_orders.down_form_order_read_service import DownFormOrderReadService
from services.down_form_orders.down_form_order_create_service import DownFormOrderCreateService
from services.down_form_orders.down_form_order_delete_service import DownFormOrderDeleteService
from services.down_form_orders.down_form_order_update_service import DownFormOrderUpdateService
# schema
from schemas.down_form_orders.down_form_order_dto import DownFormOrderDto, DownFormOrdersBulkDto
from schemas.down_form_orders.response.down_form_orders_response import (
    DownFormOrderResponse,
    DownFormOrderBulkResponse,
    DownFormOrderPaginationResponse,
    DownFormOrderBulkCreateResponse,
)
from schemas.down_form_orders.request.down_form_orders_request import (
    DownFormOrderCreateJsonRequest,
    DownFormOrderBulkCreateJsonRequest,
    DownFormOrderBulkUpdateJsonRequest,
    DownFormOrderBulkDeleteJsonRequest,
    DownFormOrderBulkCreateFilterRequest,
)
# utils
from utils.response_status import RowStatus
from utils.excels.excel_handler import ExcelHandler
from utils.logs.sabangnet_logger import get_logger
# minio
from minio_handler import upload_and_get_url, temp_file_to_object_name


logger = get_logger(__name__)


router = APIRouter(
    prefix="/down-form-order",
    tags=["down-form-order"],
)


def get_down_form_order_create_service(session: AsyncSession = Depends(get_async_session)) -> DownFormOrderCreateService:
    return DownFormOrderCreateService(session=session)


def get_down_form_order_read_service(session: AsyncSession = Depends(get_async_session)) -> DownFormOrderReadService:
    return DownFormOrderReadService(session=session)


def get_down_form_order_update_service(session: AsyncSession = Depends(get_async_session)) -> DownFormOrderUpdateService:
    return DownFormOrderUpdateService(session=session)


def get_down_form_order_delete_service(session: AsyncSession = Depends(get_async_session)) -> DownFormOrderDeleteService:
    return DownFormOrderDeleteService(session=session)


def get_data_processing_usecase(session: AsyncSession = Depends(get_async_session)) -> DataProcessingUsecase:
    return DataProcessingUsecase(session=session)


def get_down_form_order_template_usecase(session: AsyncSession = Depends(get_async_session)) -> DownFormOrderTemplateUsecase:
    return DownFormOrderTemplateUsecase(session=session)


@router.get("", response_model=DownFormOrderBulkResponse)
async def down_form_orders(
    skip: int = Query(0, ge=0, description="건너뛸 건수"),
    limit: int = Query(200, ge=1, le=200, description="조회할 건수"),
    down_form_order_read_service: DownFormOrderReadService = Depends(get_down_form_order_read_service),
):
    down_form_orders: list[DownFormOrderDto] = await down_form_order_read_service.get_down_form_orders(skip=skip, limit=limit)
    response = DownFormOrderBulkResponse(
        items=[]
    )
    logger.info(f"[down_form_orders] 요청: {skip}, {limit}")
    for down_form_order in down_form_orders:
        try:
            response.items.append(
                DownFormOrderResponse(
                    item=DownFormOrderDto.model_validate(down_form_order),
                    status=RowStatus.SUCCESS,
                    message=None
                )
            )
        except Exception as e:
            response.items.append(
                DownFormOrderResponse(
                    item=None,
                    status=RowStatus.ERROR,
                    message=str(e)
                )
            )
    return response


@router.get("/pagination", response_model=DownFormOrderPaginationResponse)
async def down_form_orders_pagination(
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=1000),
    template_code: Optional[str] = Query(
        None,
        description="form_name 필터링: 'all'은 전체, ''(빈값)은 form_name이 NULL 또는 빈 값, 그 외는 해당 값과 일치하는 항목 조회"
    ),
    down_form_order_read_service: DownFormOrderReadService = Depends(get_down_form_order_read_service),
):
    items, total = await down_form_order_read_service.get_down_form_orders_by_pagenation(page, page_size, template_code)
    dto_items: list[DownFormOrderDto] = [DownFormOrderDto.model_validate(item) for item in items]
    return DownFormOrderPaginationResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[
            DownFormOrderResponse(
                item=dto,
                status=RowStatus.SUCCESS,
                message="success"
            ) for dto in dto_items
        ]
    )


@router.post("/bulk", response_model=DownFormOrderBulkResponse)
async def bulk_create_down_form_orders(
    request: DownFormOrderBulkCreateJsonRequest,
    down_form_order_create_service: DownFormOrderCreateService = Depends(get_down_form_order_create_service),
):
    logger.info(f"[bulk_create] 요청: {request}")
    try:
        result: int = await down_form_order_create_service.bulk_create_down_form_orders(request.items)
        logger.info(f"[bulk_create] 성공: {len(request.items)}건 생성")
        return DownFormOrderBulkResponse(items=[
            DownFormOrderResponse(
                item=DownFormOrderDto.model_validate(item),
                status=RowStatus.SUCCESS,
                message="success"
            ) for item in request.items
        ])
    except Exception as e:
        logger.error(f"[bulk_create] 실패: {str(e)}", e)
        raise


@router.put("/bulk", response_model=DownFormOrderBulkResponse)
async def bulk_update_down_form_orders(
    request: DownFormOrderBulkUpdateJsonRequest,
    down_form_order_update_service: DownFormOrderUpdateService = Depends(get_down_form_order_update_service),
):
    logger.info(f"[bulk_update] 요청: {request}")
    try:
        result: int = await down_form_order_update_service.bulk_update_down_form_orders(request.items)
        logger.info(f"[bulk_update] 성공: {len(request.items)}건 수정")
        return DownFormOrderBulkResponse(items=[
            DownFormOrderResponse(
                item=DownFormOrderDto.model_validate(item),
                status=RowStatus.SUCCESS,
                message="success"
            ) for item in request.items
        ])
    except Exception as e:
        logger.error(f"[bulk_update] 실패: {str(e)}")
        raise


@router.delete("/bulk", response_model=DownFormOrderBulkResponse)
async def bulk_delete_down_form_orders(
    request: DownFormOrderBulkDeleteJsonRequest = Body(...),
    down_form_order_delete_service: DownFormOrderDeleteService = Depends(get_down_form_order_delete_service),
):
    logger.info(f"[bulk_delete] 요청: {request}")
    try:
        result: int = await down_form_order_delete_service.bulk_delete_down_form_orders(request.ids)
        logger.info(f"[bulk_delete] 성공: {len(request.ids)}건 삭제")
        return DownFormOrderBulkResponse(items=[
            DownFormOrderResponse(
                item=None,
                status=RowStatus.SUCCESS,
                message="success"
            ) for order_id in request.ids
        ])
    except Exception as e:
        logger.error(f"[bulk_delete] 실패: {str(e)}", e)
        raise


@router.delete("/all")
async def delete_all_down_form_orders(
    down_form_order_delete_service: DownFormOrderDeleteService = Depends(get_down_form_order_delete_service),
):
    try:
        await down_form_order_delete_service.delete_all_down_form_orders()
        return {"message": "모든 데이터 삭제 완료"}
    except Exception as e:
        logger.error(f"[delete_all] 실패: {str(e)}", e)
        raise


@router.delete("/duplicate")
async def delete_duplicate_down_form_orders(
    down_form_order_delete_service: DownFormOrderDeleteService = Depends(get_down_form_order_delete_service),
):
    deleted_count = await down_form_order_delete_service.delete_duplicate_down_form_orders()
    return {"message": f"중복 데이터 삭제 완료: {deleted_count}개 행 삭제됨"}


@router.post("/excel-to-minio")
async def upload_excel_file_and_get_url(
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


@router.post("/excel-to-db")
async def get_excel_to_db(
    template_code: str = Form(...),
    file: UploadFile = File(...),
    data_processing_usecase: DataProcessingUsecase = Depends(get_data_processing_usecase),
):
    """
    프론트에서 template_code와 엑셀 파일을 받아 DB에 저장
    """
    dataframe = ExcelHandler.from_upload_file_to_dataframe(file)
    saved_count = await data_processing_usecase.process_excel_to_down_form_orders(dataframe, template_code)
    return {"saved_count": saved_count}


@router.get("/example")
async def example_usage():
    return {
        "workflow": "원본 데이터 -> 템플릿별 변환 -> down_form_orders 저장",
        "step1": "POST /process-data with template_code='gmarket_erp'",
        "step2": "원본 receive_orders 데이터를 G마켓 ERP 형식으로 변환",
        "step3": "변환된 데이터를 down_form_orders에 저장",
        "step4": "GET /down-form-orders?template_code=gmarket_erp로 결과 확인",
        "example_request": {
            "template_code": "gmarket_erp",
            "filters": {
                "date_from": "2025-06-02",
                "date_to": "2025-06-06",
                "mall_id": "ESM지마켓",
                # "order_status" : "출고완료" 비우면 모든 상태 조회
            }
        }
    }


@router.post("/bulk/filter", response_model=DownFormOrderBulkCreateResponse)
async def bulk_create_down_form_orders_by_filter(
    request: DownFormOrderBulkCreateFilterRequest = Depends(),
    data_processing_usecase: DataProcessingUsecase = Depends(
        get_data_processing_usecase)
):
    try:
        template_code: str = request.template_code
        filters: dict[str, Any] = request.filters.model_dump() if request.filters else {}
        down_form_order_bulk_dto: DownFormOrdersBulkDto = await data_processing_usecase.save_down_form_orders_from_receive_orders_by_filter(filters, template_code)
        return DownFormOrderBulkCreateResponse.from_dto(down_form_order_bulk_dto)
    except Exception as e:
        return DownFormOrderBulkCreateResponse.from_dto(DownFormOrdersBulkDto(
            success=False,
            template_code=template_code,
            processed_count=0,
            saved_count=0,
            message=f"Error: {str(e)}"
        ))


@router.post("/bulk/without-filter", response_model=DownFormOrderBulkCreateResponse)
async def bulk_create_down_form_orders_without_filter(
    request: DownFormOrderCreateJsonRequest,
    down_form_order_template_usecase: DownFormOrderTemplateUsecase = Depends(
        get_down_form_order_template_usecase)
):
    try:
        template_code: str = request.template_code
        raw_data: list[dict[str, Any]] = request.raw_data
        saved_count = await down_form_order_template_usecase.process_and_save(template_code, raw_data)
        return DownFormOrderBulkCreateResponse(
            success=True,
            template_code=template_code,
            processed_count=len(raw_data),
            saved_count=saved_count,
            message="Success"
        )
    except Exception as e:
        return DownFormOrderBulkCreateResponse(
            success=False,
            template_code=template_code,
            processed_count=len(raw_data),
            saved_count=0,
            message=f"Error: {str(e)}"
        )
