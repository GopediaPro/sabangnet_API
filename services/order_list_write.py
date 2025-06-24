import json
from datetime import datetime, timezone
from repository.create_receive_order import CreateReceiveOrder
from models.receive_order.receive_order import ReceiveOrder


class OrderListWriteService:
    def __init__(self):
        self.create_receive_order = CreateReceiveOrder()

    def convert_to_model(self, order_data: dict[str, str]) -> ReceiveOrder:
        order_data = {k.lower(): v for k, v in order_data.items()}
        return ReceiveOrder(**order_data)
    
    async def create_orders(self):
        with open("./files/json/order_list.json", "r", encoding="utf-8") as f:
            order_data_list: list[dict] = json.load(f)
        for order_data in order_data_list:
            order_model = self.convert_to_model(order_data)
            await self.create_receive_order.create(obj_in=order_model)
