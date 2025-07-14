from typing import Any
from pydantic import BaseModel, Field, ConfigDict
from schemas.order.down_form_order_dto import DownFormOrderDto
from schemas.order.request.receive_orders_request import ReceiveOrdersFillterRequest


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
    template_code: str
    source_table: str = "receive_orders"

    filters: ReceiveOrdersFillterRequest = Field(..., description="필터 정보")


class DownFormOrderBulkUpdateJsonRequest(BaseModel):
    items: list[DownFormOrderDto]


class DownFormOrderBulkDeleteJsonRequest(BaseModel):
    ids: list[int]


class DownFormOrderListRequest(BaseModel):
    page: int = Field(1, description="페이지 번호")
    page_size: int = Field(100, description="페이지 크기")
    # 필터/정렬 옵션 필요시 추가
