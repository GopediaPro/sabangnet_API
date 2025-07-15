from schemas.order.order_dto import OrderDto
from models.order.down_form_order import BaseFormOrder


class BaseExportFormOrder(BaseFormOrder):
    __tablename__ = "export_form_orders"

    @classmethod
    def build_erp(cls, order_dto: OrderDto) -> "BaseExportFormOrder":
        """order 데이터 기반으로 각 케이스별 ERP 데이터 생성"""
        order_data = order_dto.model_dump()
        return cls(**order_data)
    
    @classmethod
    def build_happo(cls, order_dto_list: list[OrderDto]) -> "BaseExportFormOrder":
        """order 데이터 기반으로 각 케이스별 ERP 데이터 생성"""
        
        ...