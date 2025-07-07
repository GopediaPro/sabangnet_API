from core.db import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Request, Query
from services.order.order_read_service import OrderReadService
from schemas.order.response.order_response import OrderResponse, OrderResponseList


router = APIRouter(
    prefix="/order",
    tags=["order"],
)

def get_order_read_service(session: AsyncSession = Depends(get_async_session)) -> OrderReadService:
    return OrderReadService(session=session)


@router.get("/{idx}", response_model=OrderResponse)
async def get_order(
    request: Request,
    idx: str,
    order_read_service: OrderReadService = Depends(get_order_read_service),
):
    return OrderResponse.from_dto(await order_read_service.get_order_by_idx(idx))


@router.get("/all", response_model=OrderResponseList)
async def get_orders(
    request: Request,
    order_read_service: OrderReadService = Depends(get_order_read_service),
):
    return OrderResponseList.from_dto(await order_read_service.get_orders())


@router.get("/pagination", response_model=OrderResponseList)
async def get_orders_pagination(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1),
    order_read_service: OrderReadService = Depends(get_order_read_service),
):
    return OrderResponseList.from_dto(await order_read_service.get_orders_pagination(page, page_size))