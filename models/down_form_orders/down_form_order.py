from decimal import Decimal
from datetime import datetime
from models.base_model import Base
from sqlalchemy.orm import Mapped, mapped_column
from schemas.receive_orders.receive_orders_dto import ReceiveOrdersDto
from sqlalchemy import TIMESTAMP, Integer, String, Text, Numeric, DateTime
from sqlalchemy.dialects.postgresql import JSONB
class BaseFormOrder(Base):
    """
    다운폼/내보내기 폼 주문 테이블의 공통 ORM 매핑 모델
    """
    __abstract__ = True
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    process_dt: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=False))
    form_name: Mapped[str | None] = mapped_column(String(30))
    seq: Mapped[int | None] = mapped_column(Integer)
    idx: Mapped[str] = mapped_column(String(50), nullable=False)  # 사방넷주문번호
    # idx: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)  # 사방넷주문번호
    order_id: Mapped[str | None] = mapped_column(String(100))
    mall_order_id: Mapped[str | None] = mapped_column(Text)
    product_id: Mapped[str | None] = mapped_column(Text)
    product_name: Mapped[str | None] = mapped_column(Text)
    mall_product_id: Mapped[str | None] = mapped_column(String(50))
    item_name: Mapped[str | None] = mapped_column(String(100))
    sku_value: Mapped[str | None] = mapped_column(Text)
    sku_alias: Mapped[str | None] = mapped_column(Text)
    sku_no: Mapped[str | None] = mapped_column(Text)
    barcode: Mapped[str | None] = mapped_column(Text)
    model_name: Mapped[str | None] = mapped_column(Text)
    erp_model_name: Mapped[str | None] = mapped_column(Text)
    location_nm: Mapped[str | None] = mapped_column(Text)
    sale_cnt: Mapped[int | None] = mapped_column(Integer)
    pay_cost: Mapped[Decimal | None] = mapped_column(Numeric(30, 2))
    delv_cost: Mapped[Decimal | None] = mapped_column(Numeric(30, 2))
    total_cost: Mapped[Decimal | None] = mapped_column(Numeric(30, 2))
    total_delv_cost: Mapped[Decimal | None] = mapped_column(Numeric(30, 2))
    expected_payout: Mapped[Decimal | None] = mapped_column(Numeric(30, 2))
    etc_cost: Mapped[str | None] = mapped_column(Text)
    price_formula: Mapped[str | None] = mapped_column(String(50))
    service_fee: Mapped[Decimal | None] = mapped_column(Numeric(30, 2))
    sum_p_ea: Mapped[Decimal | None] = mapped_column(Numeric(30, 2))
    sum_expected_payout: Mapped[Decimal | None] = mapped_column(Numeric(30, 2))
    sum_pay_cost: Mapped[Decimal | None] = mapped_column(Numeric(30, 2))
    sum_delv_cost: Mapped[Decimal | None] = mapped_column(Numeric(30, 2))
    sum_total_cost: Mapped[Decimal | None] = mapped_column(Numeric(30, 2))
    receive_name: Mapped[str | None] = mapped_column(String(100))
    receive_cel: Mapped[str | None] = mapped_column(String(20))
    receive_tel: Mapped[str | None] = mapped_column(String(20))
    receive_addr: Mapped[str | None] = mapped_column(Text)
    receive_zipcode: Mapped[str | None] = mapped_column(String(15))
    delivery_payment_type: Mapped[str | None] = mapped_column(String(10))
    delv_msg: Mapped[str | None] = mapped_column(Text)
    delivery_id: Mapped[str | None] = mapped_column(Text)
    delivery_class: Mapped[str | None] = mapped_column(Text)
    free_gift: Mapped[str | None] = mapped_column(Text)
    etc_msg: Mapped[str | None] = mapped_column(Text)
    order_etc_7: Mapped[str | None] = mapped_column(Text)
    invoice_no: Mapped[str | None] = mapped_column(Text)
    fld_dsp: Mapped[str | None] = mapped_column(Text)
    order_etc_6: Mapped[str | None] = mapped_column(Text)
    order_date: Mapped[datetime | None] = mapped_column(DateTime)
    reg_date: Mapped[str | None] = mapped_column(String(14))
    ord_confirm_date: Mapped[str | None] = mapped_column(String(14))
    rtn_dt: Mapped[str | None] = mapped_column(String(14))
    chng_dt: Mapped[str | None] = mapped_column(String(14))
    delivery_confirm_date: Mapped[str | None] = mapped_column(String(14))
    cancel_dt: Mapped[str | None] = mapped_column(String(14))
    hope_delv_date: Mapped[str | None] = mapped_column(String(14))
    inv_send_dm: Mapped[str | None] = mapped_column(String(14))
    work_status: Mapped[str | None] = mapped_column(String(14))
    error_logs: Mapped[str | None] = mapped_column(JSONB, nullable=True)

    @classmethod
    def build_erp(cls, receive_orders_dto: ReceiveOrdersDto):
        order_data = receive_orders_dto.model_dump()
        return cls(
            process_dt=order_data.get('process_dt', datetime.now()),
            form_name=order_data.get('form_name', None),
            seq=order_data.get('seq', None),
            fld_dsp=order_data.get('fld_dsp', None),
            receive_name=order_data.get('receive_name', None),
            price_formula=order_data.get('price_formula', None),
            order_id=order_data.get('order_id', None),
            item_name=order_data.get('item_name', None),
            sale_cnt=order_data.get('sale_cnt', None),
            receive_cel=order_data.get('receive_cel', None),
            receive_tel=order_data.get('receive_tel', None),
            receive_addr=order_data.get('receive_addr', None),
            receive_zipcode=order_data.get('receive_zipcode', None),
            delivery_payment_type=order_data.get('delivery_payment_type', None),
            mall_product_id=order_data.get('mall_product_id', None),
            delv_msg=order_data.get('delv_msg', None),
            expected_payout=order_data.get('expected_payout', None),
            order_etc_6=order_data.get('order_etc_6', None),
            mall_order_id=order_data.get('mall_order_id', None),
            delivery_class=order_data.get('delivery_class', None),
            seller_code=order_data.get('seller_code', None),
            pay_cost=order_data.get('pay_cost', None),
            delv_cost=order_data.get('delv_cost', None),
            product_id=order_data.get('product_id', None),
            idx=order_data.get('idx'), # NOT NULL
            product_name=order_data.get('product_name', None),
            sku_value=order_data.get('sku_value', None),
            erp_model_name=order_data.get('erp_model_name', None),
            free_gift=order_data.get('free_gift', None),
            pay_cost_minus_mall_won_cost_times_sale_cnt=order_data.get('pay_cost_minus_mall_won_cost_times_sale_cnt', None),
            total_cost=order_data.get('total_cost', None),
            total_delv_cost=order_data.get('total_delv_cost', None),
            service_fee=order_data.get('service_fee', None),
            etc_msg=order_data.get('etc_msg', None),
            sum_p_ea=order_data.get('sum_p_ea', None),
            sum_expected_payout=order_data.get('sum_expected_payout', None),
            location_nm=order_data.get('location_nm', None),
            order_etc_7=order_data.get('order_etc_7', None),
            sum_pay_cost=order_data.get('sum_pay_cost', None),
            sum_delv_cost=order_data.get('sum_delv_cost', None),
            sku_alias=order_data.get('sku_alias', None),
            sum_total_cost=order_data.get('sum_total_cost', None),
            model_name=order_data.get('model_name', None),
            invoice_no=order_data.get('invoice_no', None),
            sku_no=order_data.get('sku_no', None),
            barcode=order_data.get('barcode', None),
            etc_cost=order_data.get('etc_cost', None),
            delivery_id=order_data.get('delivery_id', None),
            order_date=order_data.get('order_date', None),
            reg_date=order_data.get('reg_date', None),
            ord_confirm_date=order_data.get('ord_confirm_date', None),
            rtn_dt=order_data.get('rtn_dt', None),
            chng_dt=order_data.get('chng_dt', None),
            delivery_confirm_date=order_data.get('delivery_confirm_date', None),
            cancel_dt=order_data.get('cancel_dt', None),
            hope_delv_date=order_data.get('hope_delv_date', None),
            inv_send_dm=order_data.get('inv_send_dm', None),
            error_logs=order_data.get('error_logs', None),
        )


class BaseDownFormOrder(BaseFormOrder):
    __tablename__ = "down_form_orders"

    @classmethod
    def build_happo(cls, receive_orders_dto_list: list[ReceiveOrdersDto]) -> "BaseDownFormOrder":
        """order 데이터 기반으로 각 케이스별 ERP 데이터 생성"""
        
        ...
        
    @classmethod
    def build_erp(cls, receive_orders_dto: ReceiveOrdersDto) -> "BaseDownFormOrder":
        """order 데이터 기반으로 각 케이스별 ERP 데이터 생성"""
        order_data = receive_orders_dto.model_dump()
        return cls(**order_data)
    

class TestDownFormOrder(BaseFormOrder):
    __tablename__ = "test_down_form_orders"

    @classmethod
    def build_happo(cls, receive_orders_dto_list: list[ReceiveOrdersDto]) -> "BaseDownFormOrder":
        """order 데이터 기반으로 각 케이스별 ERP 데이터 생성"""
        
        ...
        
    @classmethod
    def build_erp(cls, receive_orders_dto: ReceiveOrdersDto) -> "BaseDownFormOrder":
        """order 데이터 기반으로 각 케이스별 ERP 데이터 생성"""
        order_data = receive_orders_dto.model_dump()
        return cls(**order_data)