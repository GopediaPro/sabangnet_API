from models.down_form_orders.down_form_order import BaseFormOrder
from schemas.receive_orders.receive_orders_dto import ReceiveOrdersDto


class BaseExportFormOrder(BaseFormOrder):
    __tablename__ = "export_form_orders"

    @classmethod
    def build_erp(cls, receive_orders_dto: ReceiveOrdersDto) -> "BaseExportFormOrder":
        """order 데이터 기반으로 각 케이스별 ERP 데이터 생성"""
        order_data = receive_orders_dto.model_dump()
        return cls(**order_data)
    
    @classmethod
    def build_happo(cls, receive_orders_dto_list: list[ReceiveOrdersDto]) -> "BaseExportFormOrder":
        """order 데이터 기반으로 각 케이스별 ERP 데이터 생성"""
        
        ...