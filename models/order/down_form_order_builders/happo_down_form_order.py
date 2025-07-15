from schemas.order.order_dto import OrderDto
from models.order.down_form_order import BaseDownFormOrder


class GmarketAuctionHappoBuilder(BaseDownFormOrder):
    """G마켓, 옥션 양식"""
    
    @classmethod
    def build_happo(cls, order_dto_list: list[OrderDto]) -> BaseDownFormOrder:
        
        sum_p_ea = 0
        sum_pay_cost = 0
        sum_expected_payout = 0

        for order_dto in order_dto_list:
            order_data = order_dto.model_dump()

            sale_cnt = order_data['sale_cnt']
            order_etc_7 = order_data['order_etc_7']

            p_ea = order_data['p_ea']

            expected_payout = order_data['mall_won_cost'] * sale_cnt
            price_formula = expected_payout + order_data['order_etc_6'] + order_data['delv_cost'] # O2 + P2 + V2
            item_name = f"{order_data['sku_alias']} {sale_cnt}개"
            delivery_payment_type = order_data['delivery_method_str']
            erp_model_name = f"{order_data['barcode']} {sale_cnt}개"

        down_form_order_model = super().build_happo(order_dto)
        down_form_order_model.price_formula = price_formula
        down_form_order_model.item_name = item_name
        down_form_order_model.delivery_payment_type = delivery_payment_type
        down_form_order_model.erp_model_name = erp_model_name

        return down_form_order_model


class DefaultHappoBuilder(BaseDownFormOrder):
    """기본양식"""
    
    ...


class BrandiHappoBuilder(BaseDownFormOrder):
    """브랜디 양식(브랜디는 ERP와 합포장 공용이라 코드는 똑같음)"""
    
    ...


class KakaoOMTShopHappoBuilder(BaseDownFormOrder):
    """카카오, OMT샵 양식"""
    
    ...
