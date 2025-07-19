# std
import os
# core
from core.db import get_async_session
# fastapi
from fastapi.responses import StreamingResponse
from fastapi import APIRouter, Depends, Query, Form
# sql
from sqlalchemy.ext.asyncio import AsyncSession
# service
from services.receive_orders.receive_order_read_service import ReceiveOrderReadService
from services.receive_orders.receive_order_create_service import ReceiveOrderCreateService
# schema
from schemas.receive_orders.request.receive_orders_request import ReceiveOrdersRequest
# utils
from schemas.receive_orders.response.receive_orders_response import (
    ReceiveOrdersResponse,
    ReceiveOrdersResponseList,
    ReceiveOrdersBulkCreateResponse,
)


router = APIRouter(
    prefix="/receive-orders",
    tags=["receive-orders"],
)


def get_receive_order_read_service(session: AsyncSession = Depends(get_async_session)) -> ReceiveOrderReadService:
    return ReceiveOrderReadService(session=session)


def get_receive_order_create_service(session: AsyncSession = Depends(get_async_session)) -> ReceiveOrderCreateService:
    return ReceiveOrderCreateService(session=session)


@router.get("/all", response_model=ReceiveOrdersResponseList)
async def get_receive_orders_all(
    skip: int = Query(0, ge=0, description="건너뛸 건수"),
    limit: int = Query(200, ge=1, le=200, description="조회할 건수"),
    order_read_service: ReceiveOrderReadService = Depends(get_receive_order_read_service),
):
    """
    주문 수집 데이터 전체 조회 (한 번에 최대 200건 까지만 조회 가능)
    """
    return ReceiveOrdersResponseList.from_dto(await order_read_service.get_orders(skip, limit))


@router.get("/pagination", response_model=ReceiveOrdersResponseList)
async def get_receive_orders_by_pagination(
    page: int = Query(1, ge=1, description="페이지 번호"),
    page_size: int = Query(20, ge=1, description="페이지 당 조회할 건수"),
    order_read_service: ReceiveOrderReadService = Depends(get_receive_order_read_service),
):
    """
    주문 수집 데이터 페이징 조회
    """
    return ReceiveOrdersResponseList.from_dto(await order_read_service.get_orders_pagination(page, page_size))


@router.get("/{idx}", response_model=ReceiveOrdersResponse)
async def get_receive_order_by_idx(
    idx: str,
    order_read_service: ReceiveOrderReadService = Depends(get_receive_order_read_service),
):
    """
    주문 수집 데이터 단건 조회
    """
    order = await order_read_service.get_order_by_idx(idx)
    if order is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="주문을 찾을 수 없습니다.")
    return ReceiveOrdersResponse.from_dto(order)


@router.post("/xml-template", response_class=StreamingResponse)
def make_and_get_receive_order_xml_template(
    request: ReceiveOrdersRequest = Form(...),
    order_create_service: ReceiveOrderCreateService = Depends(
        get_receive_order_create_service),
) -> StreamingResponse:
    """
    주문 수집 데이터 XML 템플릿만 생성하고 내려받음 (요청은 안함.)
    """
    try:
        return order_create_service.get_order_xml_template(
            ord_st_date=request.get_order_date_from_yyyymmdd(),
            ord_ed_date=request.get_end_date_yyyymmdd(),
            order_status=request.get_order_status_code()
        )
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/from-sabangnet/to-db", response_model=ReceiveOrdersBulkCreateResponse)
async def save_receive_orders_to_db(
    request: ReceiveOrdersRequest = Form(...),
    order_create_service: ReceiveOrderCreateService = Depends(
        get_receive_order_create_service),
):
    """
    주문 수집 데이터 XML 파일을 업로드하여 주문 데이터를 생성함.
    """
    try:
        xml_file_path = order_create_service.create_request_xml(
            ord_st_date=request.get_order_date_from_yyyymmdd(),
            ord_ed_date=request.get_end_date_yyyymmdd(),
            order_status=request.get_order_status_code()
        )
        xml_url = order_create_service.get_xml_url_from_minio(xml_file_path)
        xml_content = order_create_service.get_orders_from_sabangnet(xml_url)
        safe_mode = os.getenv("DEPLOY_ENV", "production") != "production"
        return await order_create_service.save_orders_to_db_from_xml(xml_content, safe_mode)
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=str(e))