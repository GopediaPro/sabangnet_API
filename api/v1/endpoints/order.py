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


@router.get("/all", response_model=OrderResponseList)
async def get_orders(
    request: Request,
    skip: int = Query(0, ge=0, description="건너뛸 건수"),
    limit: int = Query(200, ge=1, le=200, description="조회할 건수"),
    order_read_service: OrderReadService = Depends(get_order_read_service),
):
    """
    주문 수집 데이터 전체 조회 (한 번에 최대 200건 까지만 조회 가능)
    """
    return OrderResponseList.from_dto(await order_read_service.get_orders(skip, limit))


@router.get("/pagination", response_model=OrderResponseList)
async def get_orders_pagination(
    request: Request,
    page: int = Query(1, ge=1, description="페이지 번호"),
    page_size: int = Query(20, ge=1, description="페이지 당 조회할 건수"),
    order_read_service: OrderReadService = Depends(get_order_read_service),
):
    """
    주문 수집 데이터 페이징 조회
    """
    return OrderResponseList.from_dto(await order_read_service.get_orders_pagination(page, page_size))


@router.get("/{idx}", response_model=OrderResponse)
async def get_order(
    request: Request,
    idx: str,
    order_read_service: OrderReadService = Depends(get_order_read_service),
):
    """
    주문 수집 데이터 단건 조회
    """
    return OrderResponse.from_dto(await order_read_service.get_order_by_idx(idx))