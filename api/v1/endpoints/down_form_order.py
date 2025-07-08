from core.db import get_async_session
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from services.usecase.down_form_order_usecase import DownFormOrderUsecase
from services.order.down_form_order_read_service import DownFormOrderReadService
from schemas.order.request.down_form_order_request import DownFormOrderCreate, DownFormOrderRead
from schemas.order.response.down_form_order_response import DownFormOrderCreateResponse, DownFormOrderReadResponse


router = APIRouter(
    prefix="/down-form-order",
    tags=["down-form-order"],
)


def get_down_form_order_read_service(session: AsyncSession = Depends(get_async_session)) -> DownFormOrderReadService:
    return DownFormOrderReadService(session=session)


def get_down_form_order_usecase(session: AsyncSession = Depends(get_async_session)) -> DownFormOrderUsecase:
    return DownFormOrderUsecase(session=session)


@router.get("/{idx}", response_model=DownFormOrderReadResponse)
async def get_down_form_order_by_idx(
    request: DownFormOrderRead,
    down_form_order_read_service: DownFormOrderReadService = Depends(get_down_form_order_read_service),
):
    return DownFormOrderReadResponse.from_dto(await down_form_order_read_service.get_down_form_order_by_idx(request.idx))


@router.post("/{idx}", response_model=DownFormOrderCreateResponse)
async def create_down_form_order_by_order_idx(
    request: DownFormOrderCreate,
    down_form_order_usecase: DownFormOrderUsecase = Depends(get_down_form_order_usecase),
):
    return DownFormOrderCreateResponse.from_dto(await down_form_order_usecase.create_down_form_order_by_order_idx(request.idx))