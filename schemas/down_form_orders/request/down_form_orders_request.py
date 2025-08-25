from datetime import date, datetime
from typing import Any, Optional
from pydantic import BaseModel, Field, ConfigDict
from schemas.down_form_orders.down_form_order_dto import DownFormOrderDto
from schemas.receive_orders.request.receive_orders_request import (
    ReceiveOrdersFillterRequest,
    BaseDateRangeRequest,
    ReceiveOrdersFillterRequest,
    ReceiveOrdersToDownFormOrdersFillterRequst
)


class DownFormOrderCreateJsonRequest(BaseModel):
    template_code: str = Field(..., description="템플릿 코드")
    raw_data: list[dict[str, Any]] = Field(..., description="원본 주문 데이터 목록")

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "template_code": "gmarket_erp",
                    "raw_data": [
                        {
                            "form_name": "testtesttest1",
                            "seq": 111,
                            "idx": "123456789",
                            "order_id": "987654321",
                            "mall_order_id": "987654321",
                            "product_id": "test1234",
                            "product_name": "test1234test",
                            "mall_product_id": "ttttt",
                            "item_name": "아이템 테스트",
                            "sku_value": "테스트",
                            "sku_alias": "테스트test",
                        },
                        {
                            "form_name": "testtesttest2",
                            "seq": 222,
                            "idx": "t2",
                            "order_id": "t2",
                            "mall_order_id": "t2",
                            "product_id": "t2",
                            "product_name": "t2",
                            "mall_product_id": "ttttt2",
                            "item_name": "아이템 테스트2",
                            "sku_value": "테스트2",
                            "sku_alias": "테스트test2",
                        }
                    ]
                }
            ]
        }
    )


class DownFormOrderBulkCreateJsonRequest(BaseModel):
    items: list[DownFormOrderDto]


class DownFormOrderBulkCreateFilterRequest(BaseModel):
    template_code: Optional[str] = Field(None, description="템플릿 코드")
    source_table: str = "receive_orders"

    filters: Optional[ReceiveOrdersFillterRequest] = Field(
        None, description="필터 정보")


class DownFormOrderBulkUpdateJsonRequest(BaseModel):
    items: list[DownFormOrderDto]


class DownFormOrderBulkDeleteJsonRequest(BaseModel):
    ids: list[int]


class DownFormOrdersDateRangeFillterRequest(BaseDateRangeRequest):
    """
    날짜/주문상태 필수 요청 객체
    """
    # 부모 클래스의 Optional 필드들을 필수로 오버라이드
    date_from: date = Field(..., description="시작 날짜", example="2025-06-02")
    date_to: date = Field(..., description="종료 날짜", example="2025-06-06")


class DownFormOrdersPaginationWithDateRangeRequest(BaseModel):
    page: int = Field(1, ge=1, description="페이지 번호")
    page_size: int = Field(100, ge=1, le=1000, description="페이지 크기")
    filters: DownFormOrdersDateRangeFillterRequest = Field(
        ..., description="필터 정보")
    template_code: str = Field(
        ...,
        description="\
            form_name 필터링: 'all'은 전체, \
            ''(빈값)은 form_name이 NULL 또는 빈 값, 그 외는 해당 값과 일치하는 항목 조회"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "page": 1,
                    "page_size": 100,
                    "template_code": "all",
                    "filters": {
                        "date_from": "2025-06-02",
                        "date_to": "2025-06-06",
                    }
                }
            ]
        }
    )


class DownFormOrdersFromReceiveOrdersFillterRequest(BaseModel):
    filters: Optional[ReceiveOrdersToDownFormOrdersFillterRequst] = Field(
        ..., description="필터 정보")


class DbToExcelRequest(BaseModel):
    ord_st_date: datetime = Field(..., description="주문 수집 시작 날짜 및 시간")
    ord_ed_date: datetime = Field(..., description="주문 수집 종료 날짜 및 시간")
    form_names: list[str] = Field(None, description="양식 이름 목록")
