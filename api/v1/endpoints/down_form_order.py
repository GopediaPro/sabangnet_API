from core.db import get_async_session
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from services.order.down_form_order_read_service import DownFormOrderReadService
from services.order.down_form_order_create_service import DownFormOrderCreateService
from schemas.order.request.down_form_order_request import DownFormOrderCreate, DownFormOrderRead
from schemas.order.response.down_form_order_response import DownFormOrderCreateResponse, DownFormOrderReadResponse


router = APIRouter(
    prefix="/down-form-order",
    tags=["down-form-order"],
)


def get_down_form_order_create_service(session: AsyncSession = Depends(get_async_session)) -> DownFormOrderCreateService:
    return DownFormOrderCreateService(session=session)


def get_down_form_order_read_service(session: AsyncSession = Depends(get_async_session)) -> DownFormOrderReadService:
    return DownFormOrderReadService(session=session)


@router.get("/{idx}", response_model=DownFormOrderReadResponse)
async def get_down_form_order(
    request: DownFormOrderRead,
    idx: str,
    down_form_order_read_service: DownFormOrderReadService = Depends(get_down_form_order_read_service),
):
    return DownFormOrderReadResponse.from_dto(await down_form_order_read_service.get_down_form_order(idx))


@router.post("{idx}", response_model=DownFormOrderCreateResponse)
async def create_down_form_order(
    request: DownFormOrderCreate,
    down_form_order_create_service: DownFormOrderCreateService = Depends(get_down_form_order_create_service),
):
    return DownFormOrderCreateResponse.from_dto(await down_form_order_create_service.create_down_form_order(request))