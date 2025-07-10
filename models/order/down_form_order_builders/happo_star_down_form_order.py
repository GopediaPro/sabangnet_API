from schemas.order.order_dto import OrderDto
from models.order.down_form_order import BaseDownFormOrder


class StarDeliveryGmarketAuctionHappoBuilder(BaseDownFormOrder):
    """스타배송 - G마켓, 옥션 양식"""
    
    ...


class StarDeliveryDefaultHappoBuilder(BaseDownFormOrder):
    """스타배송 - 기본양식"""
    
    ...


class StarDeliveryAlwayzHappoBuilder(BaseDownFormOrder):
    """스타배송 - 올웨이즈 양식"""
    
    ...


class StarDeliveryBrandiHappoBuilder(BaseDownFormOrder):
    """스타배송 - 브랜디 양식"""
    
    ...
