# core
from core.db import get_async_session
# fastapi
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
# sql
from sqlalchemy.ext.asyncio import AsyncSession
# service
from services.order.order_read_service import OrderReadService
from services.order.order_create_service import OrderCreateService
from services.usecase.down_form_order_save_usecase import DownFormOrderSaveUsecase
from services.usecase.down_form_order_template_usecase import DownFormOrderTemplateUsecase
# schema
from schemas.order.request.receive_orders_request import ReceiveOrdersRequest
from schemas.order.response.receive_orders_response import \
ReceiveOrdersResponse,\
ReceiveOrdersResponseList,\
ReceiveOrdersBulkCreateResponse


router = APIRouter(
    prefix="/order",
    tags=["order"],
)


def get_order_read_service(session: AsyncSession = Depends(get_async_session)) -> OrderReadService:
    return OrderReadService(session=session)


def get_order_create_service(session: AsyncSession = Depends(get_async_session)) -> OrderCreateService:
    return OrderCreateService(session=session)


def get_down_form_order_template_usecase(session: AsyncSession = Depends(get_async_session)) -> DownFormOrderTemplateUsecase:
    return DownFormOrderTemplateUsecase(session=session)


def get_down_form_order_save_usecase(session: AsyncSession = Depends(get_async_session)) -> DownFormOrderSaveUsecase:
    return DownFormOrderSaveUsecase(session=session)


@router.get("/all", response_model=ReceiveOrdersResponseList)
async def get_orders(
    skip: int = Query(0, ge=0, description="건너뛸 건수"),
    limit: int = Query(200, ge=1, le=200, description="조회할 건수"),
    order_read_service: OrderReadService = Depends(get_order_read_service),
):
    """
    주문 수집 데이터 전체 조회 (한 번에 최대 200건 까지만 조회 가능)
    """
    return ReceiveOrdersResponseList.from_dto(await order_read_service.get_orders(skip, limit))


@router.get("/pagination", response_model=ReceiveOrdersResponseList)
async def get_orders_pagination(
    page: int = Query(1, ge=1, description="페이지 번호"),
    page_size: int = Query(20, ge=1, description="페이지 당 조회할 건수"),
    order_read_service: OrderReadService = Depends(get_order_read_service),
):
    """
    주문 수집 데이터 페이징 조회
    """
    return ReceiveOrdersResponseList.from_dto(await order_read_service.get_orders_pagination(page, page_size))


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
                "order_date_from": "2025-04-23",
                "order_date_to": "2025-04-30",
                "mall_id": "ESM지마켓",
                # "order_status" : "출고완료" 비우면 모든 상태 조회
            }
        }
    } 


@router.get("/{idx}", response_model=OrderResponse)
async def get_order(
    idx: str,
    order_read_service: OrderReadService = Depends(get_order_read_service),
):
    """
    주문 수집 데이터 단건 조회
    """
    return ReceiveOrdersResponse.from_dto(await order_read_service.get_order_by_idx(idx))


@router.post("/process-data", response_model=ProcessDataResponse)
async def process_data(
    request: ProcessDataRequest,
    session: AsyncSession = Depends(get_async_session)
):
    try:
        raw_data = await ReceiveOrderRepository(session).fetch_raw_data_from_receive_orders(request.filters.dict() if request.filters else {})
        if not raw_data:
            return ProcessDataResponse(
                success=False,
                template_code=request.template_code,
                processed_count=0,
                saved_count=0,
                message="No data found to process"
            )
        pipeline = DataProcessingPipeline(session)
        saved_count = await pipeline.process_raw_data_to_down_form_orders(
            raw_data,
            request.template_code
        )
        return ProcessDataResponse(
            success=True,
            template_code=request.template_code,
            processed_count=len(raw_data),
            saved_count=saved_count,
            message=f"Successfully processed {len(raw_data)} records and saved {saved_count} records"
        )
    except Exception as e:
        return ProcessDataResponse(
            success=False,
            template_code=request.template_code,
            processed_count=0,
            saved_count=0,
            message=f"Error: {str(e)}"
        )


@router.get("/down-form-orders")
async def get_down_form_orders(
    template_code: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    session: AsyncSession = Depends(get_async_session)
):
    repo = TemplateConfigRepository(session)
    data = await repo.get_down_form_orders(template_code, limit, offset)
    return {"data": data}


@router.post("/down-form-orders/process", response_model=DownFormOrderResponse)
async def process_down_form_orders(
    request: DownFormOrderRequest = Depends(),
    session: AsyncSession = Depends(get_async_session)
):
    service = DownFormOrderTemplateService(session)
    try:
        saved_count = await service.process_and_save(request.template_code, request.raw_data)
        return DownFormOrderResponse(saved_count=saved_count, message="Success")
    except Exception as e:
        return DownFormOrderResponse(saved_count=0, message=f"Error: {str(e)}")


@router.post("/order-xml-template", response_class=StreamingResponse)
def make_and_get_order_xml_template(
    request: ReceiveOrdersRequest = Depends(),
    order_create_service: OrderCreateService = Depends(
        get_order_create_service),
) -> StreamingResponse:
    """
    주문 수집 데이터 XML 템플릿만 생성하고 내려받음 (요청은 안함.)
    """
    return order_create_service.get_order_xml_template(
        ord_st_date=request.get_start_date_yyyymmdd(),
        ord_ed_date=request.get_end_date_yyyymmdd(),
        order_status=request.get_order_status_code()
    )


@router.post("/orders-from-xml", response_model=ReceiveOrdersBulkCreateResponse)
async def save_orders_to_db(
    request: ReceiveOrdersRequest = Depends(),
    order_create_service: OrderCreateService = Depends(
        get_order_create_service),
):
    """
    주문 수집 데이터 XML 파일을 업로드하여 주문 데이터를 생성함.
    """
    xml_file_path = order_create_service.create_request_xml(
        ord_st_date=request.get_start_date_yyyymmdd(),
        ord_ed_date=request.get_end_date_yyyymmdd(),
        order_status=request.get_order_status_code()
    )
    xml_url = order_create_service.get_xml_url_from_minio(xml_file_path)
    xml_content = order_create_service.get_orders_from_sabangnet(xml_url)
    return await order_create_service.save_orders_to_db_from_xml(xml_content)
