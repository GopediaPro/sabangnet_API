import re
from models.down_form_orders.down_form_order import BaseDownFormOrder
from schemas.receive_orders.receive_orders_dto import ReceiveOrdersDto

class GmarketAuctionErpDownFormOrder(BaseDownFormOrder):
    """G마켓, 옥션 양식"""
    
    @classmethod
    def build_erp(cls, receive_orders_dto: ReceiveOrdersDto) -> BaseDownFormOrder:
        # 추출하기 위해 dict로 변환
        order_data = receive_orders_dto.model_dump()

        sale_cnt = order_data['sale_cnt']
        expected_payout = order_data['mall_won_cost'] * sale_cnt
        price_formula = expected_payout + order_data['order_etc_6'] + order_data['delv_cost'] # O2 + P2 + V2
        item_name = f"{order_data['sku_alias']} {sale_cnt}개"
        delivery_method_str = order_data['delivery_method_str']
        erp_model_name = f"{order_data['barcode']} {sale_cnt}개"

        down_form_order_model = super().build_erp(receive_orders_dto)
        down_form_order_model.price_formula = price_formula
        down_form_order_model.item_name = item_name
        down_form_order_model.delivery_method_str = delivery_method_str
        down_form_order_model.erp_model_name = erp_model_name

        return down_form_order_model


class DefaultErpDownFormOrder(BaseDownFormOrder):
    """기본양식"""
    
    ...
    

class BrandiErpDownFormOrder(BaseDownFormOrder):
    """브랜디 양식(브랜디는 ERP와 합포장 공용)"""
    
    ...


class AlwayzErpDownFormOrder(BaseDownFormOrder):
    """올웨이즈 양식"""
    
    ...


class KakaoOMTShopErpDownFormOrder(BaseDownFormOrder):
    """카카오, OMT샵 양식"""
    
    ...


class ErpFactory:
    """ERP 양식 팩토리 클래스"""
    
    _models: dict[str, type[BaseDownFormOrder]] = {
        'G마켓2.0': GmarketAuctionErpDownFormOrder,
        '옥션2.0': GmarketAuctionErpDownFormOrder,
        '기본양식': DefaultErpDownFormOrder,
        '브랜디': BrandiErpDownFormOrder,
        # '올웨이즈': AlwayzErpDownFormOrder(), -> 사용안함
        '지그재그': KakaoOMTShopErpDownFormOrder,
        '카카오선물하기': KakaoOMTShopErpDownFormOrder,
        '카카오톡스토어': KakaoOMTShopErpDownFormOrder,
    }
    
    @classmethod
    def create_order(cls, receive_orders_dto: ReceiveOrdersDto) -> BaseDownFormOrder:
        """
        쇼핑몰에 따라 적절한 ERP 양식 객체 생성
        
        Args:
            order_dto: 주문 데이터
            
        Returns:
            DownFormOrder: 생성된 다운폼 모델 객체
        """
        extracted_fld_dsp: str = re.sub(r'\[.*?\]', '', receive_orders_dto.fld_dsp)
        cleaned_fld_dsp = extracted_fld_dsp.strip()
        down_form_orders: BaseDownFormOrder = cls._models.get(cleaned_fld_dsp, cls._models['기본양식'])
        return down_form_orders.build_erp(receive_orders_dto)
    
    @classmethod
    def get_supported_sites(cls) -> list[str]:
        """지원되는 쇼핑몰 목록 반환"""
        return list(cls._models.keys())
    
    @classmethod
    def register_model(cls, mall_type: str, model_type: type[BaseDownFormOrder]):
        """새로운 다운폼 모델 등록"""
        cls._models[mall_type.lower()] = model_type
