from decimal import Decimal
from datetime import datetime
from models.base_model import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import TIMESTAMP, Integer, String, Text, Numeric



class DownFormOrder(Base):
    """
    다운폼 주문 테이블(down_form_orders)의 ORM 매핑 모델
    """

    __tablename__ = "down_form_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    process_dt: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=False))
    form_name: Mapped[str | None] = mapped_column(String(30))
    seq: Mapped[int | None] = mapped_column(Integer)
    idx: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)  # 사방넷주문번호
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
    etc_cost: Mapped[Decimal | None] = mapped_column(Numeric(30, 2))
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
    invoice_no: Mapped[str | None] = mapped_column(Text)
    fld_dsp: Mapped[str | None] = mapped_column(Text)
    order_etc_6: Mapped[str | None] = mapped_column(Text)
    order_etc_7: Mapped[str | None] = mapped_column(Text)
    etc_msg: Mapped[str | None] = mapped_column(Text)
    free_gift: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=False), default=datetime.now)
    updated_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=False), default=datetime.now)
