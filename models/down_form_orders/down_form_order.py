from decimal import Decimal
from datetime import datetime
from models.base_model import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Integer, String, Text, Numeric, DateTime, UniqueConstraint
from schemas.receive_orders.receive_orders_dto import ReceiveOrdersDto


class BaseFormOrder(Base):
    """
    다운폼/내보내기 폼 주문 테이블의 공통 ORM 매핑 모델
    """

    __abstract__ = True

    # 기본 정보
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    process_dt: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    form_name: Mapped[str | None] = mapped_column(String(30))
    seq: Mapped[int | None] = mapped_column(Integer)
    idx: Mapped[str] = mapped_column(Text, nullable=False)  # 사방넷주문번호
    # idx: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)  # 사방넷주문번호
    order_id: Mapped[str | None] = mapped_column(String(100))
    mall_order_id: Mapped[str | None] = mapped_column(Text)

    # 상품 정보
    product_id: Mapped[str | None] = mapped_column(Text)
    product_name: Mapped[str | None] = mapped_column(Text)
    mall_product_id: Mapped[str | None] = mapped_column(Text)
    item_name: Mapped[str | None] = mapped_column(Text)
    sku_value: Mapped[str | None] = mapped_column(Text)
    sku_alias: Mapped[str | None] = mapped_column(Text)
    sku_no: Mapped[str | None] = mapped_column(Text)
    barcode: Mapped[str | None] = mapped_column(Text)
    model_name: Mapped[str | None] = mapped_column(Text)
    erp_model_name: Mapped[str | None] = mapped_column(Text)
    location_nm: Mapped[str | None] = mapped_column(Text)
    sku_id: Mapped[str | None] = mapped_column(Text)

    # 수량 및 판매 정보
    sale_cnt: Mapped[str | None] = mapped_column(String(25))

    # 금액 정보
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

    # 수취인 정보
    receive_name: Mapped[str | None] = mapped_column(String(100))
    receive_cel: Mapped[str | None] = mapped_column(String(25))
    receive_tel: Mapped[str | None] = mapped_column(String(25))
    receive_addr: Mapped[str | None] = mapped_column(Text)
    receive_zipcode: Mapped[str | None] = mapped_column(String(15))
    mall_user_id: Mapped[str | None] = mapped_column(Text)

    # 배송 정보
    delivery_payment_type: Mapped[str | None] = mapped_column(String(50))
    delv_msg: Mapped[str | None] = mapped_column(Text)
    delivery_id: Mapped[str | None] = mapped_column(Text)
    delivery_class: Mapped[str | None] = mapped_column(Text)
    invoice_no: Mapped[str | None] = mapped_column(Text)
    delivery_method_str: Mapped[str | None] = mapped_column(
        String(100)
    )  # 배송구분 ex; 선불, 무료, 선결제

    # 메시지 및 기타 정보
    free_gift: Mapped[str | None] = mapped_column(Text)
    etc_msg: Mapped[str | None] = mapped_column(Text)
    order_etc_7: Mapped[str | None] = mapped_column(Text)
    fld_dsp: Mapped[str | None] = mapped_column(Text)
    order_etc_6: Mapped[str | None] = mapped_column(Text)
    order_etc_9: Mapped[str | None] = mapped_column(Text)  # 주문일자 + 시간 (추정 컬럼)

    # 날짜 정보
    order_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )  # 주문일자
    reg_date: Mapped[str | None] = mapped_column(String(14))  # 수집일자
    ord_confirm_date: Mapped[str | None] = mapped_column(String(14))
    rtn_dt: Mapped[str | None] = mapped_column(String(14))  # 반품일자
    chng_dt: Mapped[str | None] = mapped_column(String(14))  # 변경일자
    delivery_confirm_date: Mapped[str | None] = mapped_column(
        String(14)
    )  # 배송확인일자
    cancel_dt: Mapped[str | None] = mapped_column(String(14))  # 취소일자
    hope_delv_date: Mapped[str | None] = mapped_column(String(14))  # 배송희망일자
    inv_send_dm: Mapped[str | None] = mapped_column(String(14))  # 송장전송일자

    # 처리 상태 및 로그
    work_status: Mapped[str | None] = mapped_column(String(14))
    error_logs: Mapped[str | None] = mapped_column(JSONB, nullable=True)
    batch_id: Mapped[int | None] = mapped_column(Integer)

    @classmethod
    def build_erp(cls, receive_orders_dto: ReceiveOrdersDto):
        order_data = receive_orders_dto.model_dump()
        return cls(
            process_dt=order_data.get("process_dt", datetime.now()),
            form_name=order_data.get("form_name", None),
            seq=order_data.get("seq", None),
            fld_dsp=order_data.get("fld_dsp", None),
            receive_name=order_data.get("receive_name", None),
            price_formula=order_data.get("price_formula", None),
            order_id=order_data.get("order_id", None),
            item_name=order_data.get("item_name", None),
            sale_cnt=order_data.get("sale_cnt", None),
            receive_cel=order_data.get("receive_cel", None),
            receive_tel=order_data.get("receive_tel", None),
            receive_addr=order_data.get("receive_addr", None),
            receive_zipcode=order_data.get("receive_zipcode", None),
            delivery_payment_type=order_data.get("delivery_payment_type", None),
            mall_product_id=order_data.get("mall_product_id", None),
            delv_msg=order_data.get("delv_msg", None),
            expected_payout=order_data.get("expected_payout", None),
            order_etc_6=order_data.get("order_etc_6", None),
            mall_order_id=order_data.get("mall_order_id", None),
            delivery_class=order_data.get("delivery_class", None),
            seller_code=order_data.get("seller_code", None),
            pay_cost=order_data.get("pay_cost", None),
            delv_cost=order_data.get("delv_cost", None),
            product_id=order_data.get("product_id", None),
            idx=order_data.get("idx"),  # NOT NULL
            product_name=order_data.get("product_name", None),
            sku_value=order_data.get("sku_value", None),
            erp_model_name=order_data.get("erp_model_name", None),
            free_gift=order_data.get("free_gift", None),
            pay_cost_minus_mall_won_cost_times_sale_cnt=order_data.get(
                "pay_cost_minus_mall_won_cost_times_sale_cnt", None
            ),
            total_cost=order_data.get("total_cost", None),
            total_delv_cost=order_data.get("total_delv_cost", None),
            service_fee=order_data.get("service_fee", None),
            etc_msg=order_data.get("etc_msg", None),
            sum_p_ea=order_data.get("sum_p_ea", None),
            sum_expected_payout=order_data.get("sum_expected_payout", None),
            location_nm=order_data.get("location_nm", None),
            order_etc_7=order_data.get("order_etc_7", None),
            sum_pay_cost=order_data.get("sum_pay_cost", None),
            sum_delv_cost=order_data.get("sum_delv_cost", None),
            sku_alias=order_data.get("sku_alias", None),
            sum_total_cost=order_data.get("sum_total_cost", None),
            model_name=order_data.get("model_name", None),
            invoice_no=order_data.get("invoice_no", None),
            sku_no=order_data.get("sku_no", None),
            barcode=order_data.get("barcode", None),
            etc_cost=order_data.get("etc_cost", None),
            delivery_id=order_data.get("delivery_id", None),
            order_date=order_data.get("order_date", None),
            reg_date=order_data.get("reg_date", None),
            ord_confirm_date=order_data.get("ord_confirm_date", None),
            rtn_dt=order_data.get("rtn_dt", None),
            chng_dt=order_data.get("chng_dt", None),
            delivery_confirm_date=order_data.get("delivery_confirm_date", None),
            cancel_dt=order_data.get("cancel_dt", None),
            hope_delv_date=order_data.get("hope_delv_date", None),
            inv_send_dm=order_data.get("inv_send_dm", None),
            error_logs=order_data.get("error_logs", None),
        )


class BaseDownFormOrder(BaseFormOrder):
    __tablename__ = "down_form_orders"

    __table_args__ = (UniqueConstraint("idx", name="uq_down_form_orders_idx"),)

    @classmethod
    def build_happo(
        cls, receive_orders_dto_list: list[ReceiveOrdersDto]
    ) -> "BaseDownFormOrder":
        """order 데이터 기반으로 각 케이스별 ERP 데이터 생성"""

        ...

    @classmethod
    def build_erp(cls, receive_orders_dto: ReceiveOrdersDto) -> "BaseDownFormOrder":
        """order 데이터 기반으로 각 케이스별 ERP 데이터 생성"""
        order_data = receive_orders_dto.model_dump()
        return cls(**order_data)
