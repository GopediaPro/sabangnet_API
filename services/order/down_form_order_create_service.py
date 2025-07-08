from typing import Any
from decimal import Decimal
from datetime import datetime
from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession
from models.order.down_form_order import DownFormOrder
from schemas.order.down_form_order_dto import DownFormOrderDto
from repository.down_form_order_repository import DownFormOrderRepository


class DownFormOrderCreateService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.down_form_order_repository = DownFormOrderRepository(session)

    async def create_down_form_order(self, idx: str) -> DownFormOrderDto:
        return await self.down_form_order_repository.create_down_form_order(DownFormOrderDto(idx=idx))


class DownFormOrderBuilder(ABC):
    """다운폼 주문 생성을 위한 추상 빌더 클래스"""
    
    @abstractmethod
    def erp_build(self, base_data: dict[str, Any]) -> DownFormOrder:
        """order 데이터 기반으로 각 케이스별 ERP 데이터 생성"""
        pass

    @abstractmethod
    def happo_build(self, erp_data: dict[str, Any]) -> DownFormOrder:
        """ERP 데이터 기반으로 각 케이스별 합포장 데이터 생성"""
        pass


class DefaultDownFormOrderBuilder(DownFormOrderBuilder):
    """기본 다운폼 주문 빌더"""
    
    def erp_build(self, base_data: dict[str, Any]) -> DownFormOrder:
        return DownFormOrder(
            process_dt=base_data.get('process_dt', datetime.now()),
            form_name=base_data.get('form_name'),
            seq=base_data.get('seq'),
            fld_dsp=base_data.get('fld_dsp'),
            receive_name=base_data.get('receive_name'),
            price_formula=base_data.get('price_formula'),
            order_id=base_data.get('order_id'),
            item_name=base_data.get('item_name'),
            sale_cnt=base_data.get('sale_cnt', 1),
            receive_cel=base_data.get('receive_cel'),
            receive_tel=base_data.get('receive_tel'),
            receive_addr=base_data.get('receive_addr'),
            receive_zipcode=base_data.get('receive_zipcode'),
            delivery_payment_type=base_data.get('delivery_payment_type'),
            mall_product_id=base_data.get('mall_product_id'),
            delv_msg=base_data.get('delv_msg'),
            expected_payout=base_data.get('expected_payout'),
            order_etc_6=base_data.get('order_etc_6'),
            mall_order_id=base_data.get('mall_order_id'),
            delivery_no=base_data.get('delivery_no'),
            delivery_class=base_data.get('delivery_class'),
            seller_code=base_data.get('seller_code'),
            pay_cost=base_data.get('pay_cost'),
            delv_cost=base_data.get('delv_cost'),
            product_id=base_data.get('product_id'),
            idx=base_data.get('idx'),
            product_name=base_data.get('product_name'),
            sku_value=base_data.get('sku_value'),
            erp_model_name=base_data.get('erp_model_name'),
            free_gift=base_data.get('free_gift'),
            pay_cost_minus_mall_won_cost_times_sale_cnt=base_data.get('pay_cost_minus_mall_won_cost_times_sale_cnt'),
            total_cost=base_data.get('total_cost'),
            total_delv_cost=base_data.get('total_delv_cost'),
            service_fee=base_data.get('service_fee'),
            etc_msg=base_data.get('etc_msg'),
            sum_p_ea=base_data.get('sum_p_ea'),
            sum_expected_payout=base_data.get('sum_expected_payout'),
            location_nm=base_data.get('location_nm'),
            order_etc_7=base_data.get('order_etc_7'),
            sum_pay_cost=base_data.get('sum_pay_cost'),
            sum_delv_cost=base_data.get('sum_delv_cost'),
            sku_alias=base_data.get('sku_alias'),
            sum_total_cost=base_data.get('sum_total_cost'),
            model_name=base_data.get('model_name'),
            invoice_no=base_data.get('invoice_no'),
            sku_no=base_data.get('sku_no'),
            barcode=base_data.get('barcode')
        )
    
    def happo_build(self, erp_data: dict[str, Any]) -> DownFormOrder:
        return DownFormOrder(
            process_dt=erp_data.get('process_dt', datetime.now()),
            form_name=erp_data.get('form_name'),
            seq=erp_data.get('seq'),
            fld_dsp=erp_data.get('fld_dsp'),
            receive_name=erp_data.get('receive_name'),
            price_formula=erp_data.get('price_formula'),
            order_id=erp_data.get('order_id'),
            item_name=erp_data.get('item_name'),
            sale_cnt=erp_data.get('sale_cnt', 1),
            receive_cel=erp_data.get('receive_cel'),
            receive_tel=erp_data.get('receive_tel'),
            receive_addr=erp_data.get('receive_addr'),
            receive_zipcode=erp_data.get('receive_zipcode'),
            delivery_payment_type=erp_data.get('delivery_payment_type'),
            mall_product_id=erp_data.get('mall_product_id'),
            delv_msg=erp_data.get('delv_msg'),
            expected_payout=erp_data.get('expected_payout'),
            order_etc_6=erp_data.get('order_etc_6'),
            mall_order_id=erp_data.get('mall_order_id'),
            delivery_no=erp_data.get('delivery_no'),
            delivery_class=erp_data.get('delivery_class'),
            seller_code=erp_data.get('seller_code'),
            pay_cost=erp_data.get('pay_cost'),
            delv_cost=erp_data.get('delv_cost'),
            product_id=erp_data.get('product_id'),
            idx=erp_data.get('idx'),
            product_name=erp_data.get('product_name'),
            sku_value=erp_data.get('sku_value'),
            erp_model_name=erp_data.get('erp_model_name'),
            free_gift=erp_data.get('free_gift'),
            pay_cost_minus_mall_won_cost_times_sale_cnt=erp_data.get('pay_cost_minus_mall_won_cost_times_sale_cnt'),
            total_cost=erp_data.get('total_cost'),
            total_delv_cost=erp_data.get('total_delv_cost'),
            service_fee=erp_data.get('service_fee'),
            etc_msg=erp_data.get('etc_msg'),
            sum_p_ea=erp_data.get('sum_p_ea'),
            sum_expected_payout=erp_data.get('sum_expected_payout'),
            location_nm=erp_data.get('location_nm'),
            order_etc_7=erp_data.get('order_etc_7'),
            sum_pay_cost=erp_data.get('sum_pay_cost'),
            sum_delv_cost=erp_data.get('sum_delv_cost'),
            sku_alias=erp_data.get('sku_alias'),
            sum_total_cost=erp_data.get('sum_total_cost'),
            model_name=erp_data.get('model_name'),
            invoice_no=erp_data.get('invoice_no'),
            sku_no=erp_data.get('sku_no'),
            barcode=erp_data.get('barcode')
        )


class GmarketDownFormOrderBuilder(DownFormOrderBuilder):
    """G마켓, 옥션 다운폼 빌더"""
    
    def erp_build(self, base_data: dict[str, Any]) -> DownFormOrder:
        # G마켓 특화 로직
        enhanced_data = base_data.copy()
        enhanced_data['fld_dsp'] = 'G마켓'
        enhanced_data['delivery_payment_type'] = '01'  # G마켓 기본 배송비 타입
        enhanced_data['form_name'] = 'GMARKET_ORDER'
        
        # G마켓 특화 필드 계산
        if enhanced_data.get('pay_cost') and enhanced_data.get('sale_cnt'):
            enhanced_data['total_cost'] = enhanced_data['pay_cost'] * enhanced_data['sale_cnt']
        
        return DefaultDownFormOrderBuilder().build(enhanced_data)


class CoupangDownFormOrderBuilder(DownFormOrderBuilder):
    """쿠팡 다운폼 빌더"""
    
    def erp_build(self, base_data: dict[str, Any]) -> DownFormOrder:
        # 쿠팡 특화 로직
        enhanced_data = base_data.copy()
        enhanced_data['fld_dsp'] = '쿠팡'
        enhanced_data['delivery_payment_type'] = '02'  # 쿠팡 기본 배송비 타입
        enhanced_data['form_name'] = 'COUPANG_ORDER'
        
        # 쿠팡 특화 필드 계산
        if enhanced_data.get('expected_payout'):
            enhanced_data['service_fee'] = str(enhanced_data['expected_payout'] * Decimal('0.05'))  # 5% 수수료
        
        return DefaultDownFormOrderBuilder().build(enhanced_data)


class NaverDownFormOrderBuilder(DownFormOrderBuilder):
    """네이버 다운폼 주문 빌더"""
    
    def erp_build(self, base_data: dict[str, Any]) -> DownFormOrder:
        # 네이버 특화 로직
        enhanced_data = base_data.copy()
        enhanced_data['fld_dsp'] = '네이버'
        enhanced_data['delivery_payment_type'] = '03'  # 네이버 기본 배송비 타입
        enhanced_data['form_name'] = 'NAVER_ORDER'
        
        return DefaultDownFormOrderBuilder().build(enhanced_data)


class DownFormOrderFactory:
    """다운폼 주문 팩토리 클래스"""
    
    _builders: dict[str, DownFormOrderBuilder] = {
        'default': DefaultDownFormOrderBuilder(),
        'gmarket': GmarketDownFormOrderBuilder(),
        'coupang': CoupangDownFormOrderBuilder(),
        'naver': NaverDownFormOrderBuilder(),
        # 추가 케이스들...
        'auction': DefaultDownFormOrderBuilder(),  # 임시로 기본 빌더 사용
        'interpark': DefaultDownFormOrderBuilder(),
        'tmon': DefaultDownFormOrderBuilder(),
        'wemakeprice': DefaultDownFormOrderBuilder(),
        'lotte': DefaultDownFormOrderBuilder(),
        'ssg': DefaultDownFormOrderBuilder(),
        'kakao': DefaultDownFormOrderBuilder(),
        'zigzag': DefaultDownFormOrderBuilder(),
    }
    
    @classmethod
    def create_order(cls, site_type: str, base_data: dict[str, Any]) -> DownFormOrder:
        """
        사이트 타입에 따라 적절한 다운폼 주문 객체 생성
        
        Args:
            site_type: 사이트 타입 (gmarket, coupang, naver 등)
            base_data: 기본 주문 데이터
            
        Returns:
            DownFormOrder: 생성된 다운폼 주문 객체
        """
        builder = cls._builders.get(site_type.lower(), cls._builders['default'])
        return builder.build(base_data)
    
    @classmethod
    def get_supported_sites(cls) -> list[str]:
        """지원되는 사이트 목록 반환"""
        return list(cls._builders.keys())
    
    @classmethod
    def register_builder(cls, site_type: str, builder: DownFormOrderBuilder):
        """새로운 빌더 등록"""
        cls._builders[site_type.lower()] = builder


# 사용 예시
def create_down_form_orders_by_site(order_data: DownFormOrderDto) -> dict[str, DownFormOrder]:
    """
    사이트별 다운폼 주문 생성 예시
    
    Args:
        order_data: 기본 주문 데이터
        
    Returns:
        Dict[str, DownFormOrder]: 사이트별 생성된 주문 객체들
    """
    base_data = order_data.model_dump()
    orders = {}
    
    # 필요한 사이트들만 선택해서 주문 생성
    required_sites = ['gmarket', 'coupang', 'naver']
    
    for site in required_sites:
        orders[site] = DownFormOrderFactory.create_order(site, base_data)
    
    return orders 