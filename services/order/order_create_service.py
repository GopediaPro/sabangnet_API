import json
from datetime import datetime, timezone

from repository.receive_order_repository import ReceiveOrderRepository
from models.order.receive_order import ReceiveOrder


class OrderListCreateService:
    def __init__(self):
        self.create_receive_order = ReceiveOrderRepository()

    def convert_to_model(self, order_data: dict[str, str]) -> ReceiveOrder:
        order_data = {k.lower(): v for k, v in order_data.items()}
        return ReceiveOrder(**order_data)
    
    async def create_orders(self):
        with open("./files/json/order_list.json", "r", encoding="utf-8") as f:
            order_data_list: list[dict] = json.load(f)
        for order_data in order_data_list:
            order_model = self.convert_to_model(order_data)
            await self.create_receive_order.create(obj_in=order_model)

    async def create_orders_from_xml(self, xml_content: str) -> int:
        """
        Parse the given XML content and insert orders into the DB using OrderListFetchService.
        Returns the number of inserted records.
        """
        from services.order.order_cli_service import OrderListFetchService
        fetch_service = OrderListFetchService(
            ord_st_date="",  # Not needed for this context
            ord_ed_date="",
            order_status=""
        )
        inserted = await fetch_service.parse_response_xml_to_db(xml_content)
        return inserted
