from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from core.db import get_async_session
from services.order.down_form_order_read_service import DownFormOrderReadService
from services.order.down_form_order_create_service import DownFormOrderCreateService
from schemas.order.request.down_form_order_request import DownFormOrderCreate, DownFormOrderUpdate, DownFormOrderDelete
from schemas.order.response.down_form_order_response import DownFormOrderListResponse, DownFormOrderBulkResponse
from schemas.order.down_form_order_dto import DownFormOrderDto
from utils.response_status import make_row_result, RowStatus

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
    down_form_order_read_service: DownFormOrderReadService = Depends(get_down_form_order_read_service),
):
    items, total = await down_form_order_read_service.get_down_form_orders_paginated(page, page_size)
    return DownFormOrderListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[DownFormOrderDto.model_validate(item) for item in items]
    )

@router.post("/bulk", response_model=DownFormOrderBulkResponse)
async def bulk_create_down_form_orders(
    request: DownFormOrderCreate,
    down_form_order_create_service: DownFormOrderCreateService = Depends(get_down_form_order_create_service),
):
    result = await down_form_order_create_service.bulk_create_down_form_orders(request.items)
    return DownFormOrderBulkResponse(results=[make_row_result(
        id=None, status=RowStatus.SUCCESS, message=None) for _ in request.items])

@router.put("/bulk", response_model=DownFormOrderBulkResponse)
async def bulk_update_down_form_orders(
    request: DownFormOrderUpdate,
    down_form_order_create_service: DownFormOrderCreateService = Depends(get_down_form_order_create_service),
):
    result = await down_form_order_create_service.bulk_update_down_form_orders(request.items)
    return DownFormOrderBulkResponse(results=[make_row_result(
        id=item.id, status=RowStatus.SUCCESS, message=None) for item in request.items])

@router.delete("/bulk", response_model=DownFormOrderBulkResponse)
async def bulk_delete_down_form_orders(
    request: DownFormOrderDelete = Body(...),
    down_form_order_create_service: DownFormOrderCreateService = Depends(get_down_form_order_create_service),
):
    result = await down_form_order_create_service.bulk_delete_down_form_orders(request.ids)
    return DownFormOrderBulkResponse(results=[make_row_result(
        id=id, status=RowStatus.SUCCESS, message=None) for id in request.ids])