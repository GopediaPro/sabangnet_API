from core.db import get_async_session
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Request, Query
from services.order.order_read_service import OrderReadService
from services.order.order_create_service import OrderCreateService
from schemas.order.request.order_xml_template_request import OrderXmlTemplateRequest
from schemas.order.response.order_response import OrderResponse, OrderResponseList, OrderBulkCreateResponse


router = APIRouter(
    prefix="/order",
    tags=["order"],
)

def get_order_read_service(session: AsyncSession = Depends(get_async_session)) -> OrderReadService:
    return OrderReadService(session=session)


def get_order_create_service(session: AsyncSession = Depends(get_async_session)) -> OrderCreateService:
    return OrderCreateService(session=session)


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


@router.post("/order-xml-template", response_class=StreamingResponse)
def make_and_get_order_xml_template(
    request: OrderXmlTemplateRequest,
    order_create_service: OrderCreateService = Depends(get_order_create_service),
) -> StreamingResponse:
    """
    주문 수집 데이터 XML 템플릿만 생성하고 내려받음 (요청은 안함.)
    """
    return order_create_service.get_order_xml_template(
        ord_st_date=request.start_date,
        ord_ed_date=request.end_date,
        order_status=request.order_status
    )


@router.post("/orders-from-xml", response_model=OrderBulkCreateResponse)
async def save_orders_to_db(
    request: OrderXmlTemplateRequest,
    order_create_service: OrderCreateService = Depends(get_order_create_service),
):
    """
    주문 수집 데이터 XML 파일을 업로드하여 주문 데이터를 생성함.
    """
    xml_file_path = order_create_service.create_request_xml(
        ord_st_date=request.start_date,
        ord_ed_date=request.end_date,
        order_status=request.order_status
    )
    xml_url = order_create_service.get_xml_url_from_minio(xml_file_path)
    xml_content = order_create_service.get_orders_from_sabangnet(xml_url)
    return await order_create_service.save_orders_to_db_from_xml(xml_content)