from typing import Any
from decimal import Decimal
from datetime import datetime

from sqlalchemy import (
    TIMESTAMP, Date, Integer, Numeric, String, Text
)
from sqlalchemy.orm import Mapped, mapped_column

from models.base_model import Base


class ReceiveOrders(Base):
    """
    주문 수집 테이블(receive_orders)의 ORM 매핑 모델
    """
    __tablename__ = "receive_orders"

    # 기본 정보
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    receive_dt: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=False))
    idx: Mapped[str] = mapped_column(String(50), unique=True)
    order_id: Mapped[str | None] = mapped_column(String(100))
    mall_id: Mapped[str | None] = mapped_column(String(100))
    mall_user_id: Mapped[str | None] = mapped_column(String(100))
    mall_user_id2: Mapped[str | None] = mapped_column(String(100))
    order_status: Mapped[str | None] = mapped_column(String(50))

    # 주문자 정보
    user_id: Mapped[str | None] = mapped_column(String(100))
    user_name: Mapped[str | None] = mapped_column(String(100))
    user_tel: Mapped[str | None] = mapped_column(String(20))
    user_cel: Mapped[str | None] = mapped_column(String(20))
    user_email: Mapped[str | None] = mapped_column(String(200))

    # 수취인 정보
    receive_name: Mapped[str | None] = mapped_column(String(100))
    receive_tel: Mapped[str | None] = mapped_column(String(25))
    receive_cel: Mapped[str | None] = mapped_column(String(25))
    receive_email: Mapped[str | None] = mapped_column(String(200))
    receive_zipcode: Mapped[str | None] = mapped_column(String(10))
    receive_addr: Mapped[str | None] = mapped_column(Text)

    # 배송 및 메세지
    delv_msg: Mapped[str | None] = mapped_column(Text)
    delv_msg1: Mapped[str | None] = mapped_column(Text)
    mul_delv_msg: Mapped[str | None] = mapped_column(Text)
    etc_msg: Mapped[str | None] = mapped_column(Text)

    # 금액 정보
    total_cost: Mapped[Decimal | None] = mapped_column(Numeric(15, 2))
    pay_cost: Mapped[Decimal | None] = mapped_column(Numeric(15, 2))
    sale_cost: Mapped[Decimal | None] = mapped_column(Numeric(15, 2))
    mall_won_cost: Mapped[Decimal | None] = mapped_column(Numeric(15, 2))
    won_cost: Mapped[Decimal | None] = mapped_column(Numeric(15, 2))
    delv_cost: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))

    # 날짜 정보
    order_date: Mapped[datetime | None] = mapped_column(Date)
    reg_date: Mapped[str | None] = mapped_column(String(14))
    ord_confirm_date: Mapped[str | None] = mapped_column(String(14))
    rtn_dt: Mapped[str | None] = mapped_column(String(14))
    chng_dt: Mapped[str | None] = mapped_column(String(14))
    delivery_confirm_date: Mapped[str | None] = mapped_column(String(14))
    cancel_dt: Mapped[str | None] = mapped_column(String(14))
    hope_delv_date: Mapped[str | None] = mapped_column(String(14))
    inv_send_dm: Mapped[str | None] = mapped_column(String(14))

    # 업체 정보
    partner_id: Mapped[str | None] = mapped_column(String(100))
    dpartner_id: Mapped[str | None] = mapped_column(String(100))

    # 상품 정보
    mall_product_id: Mapped[str | None] = mapped_column(String(100))
    product_id: Mapped[str | None] = mapped_column(String(100))
    sku_id: Mapped[str | None] = mapped_column(String(100))
    p_product_name: Mapped[str | None] = mapped_column(Text)
    p_sku_value: Mapped[str | None] = mapped_column(Text)
    product_name: Mapped[str | None] = mapped_column(Text)
    sku_value: Mapped[str | None] = mapped_column(Text)
    compayny_goods_cd: Mapped[str | None] = mapped_column(String(255))
    sku_alias: Mapped[str | None] = mapped_column(String(200))
    goods_nm_pr: Mapped[str | None] = mapped_column(Text)
    goods_keyword: Mapped[str | None] = mapped_column(String(255))
    model_no: Mapped[str | None] = mapped_column(String(255))
    model_name: Mapped[str | None] = mapped_column(String(255))
    barcode: Mapped[str | None] = mapped_column(String(100))

    # 수량 및 구분 정보
    sale_cnt: Mapped[int | None] = mapped_column(Integer)
    box_ea: Mapped[int | None] = mapped_column(Integer)
    p_ea: Mapped[int | None] = mapped_column(Integer)
    delivery_method_str: Mapped[str | None] = mapped_column(String(100))
    delivery_method_str2: Mapped[str | None] = mapped_column(String(100))
    order_gubun: Mapped[str | None] = mapped_column(String(10))
    set_gubun: Mapped[str | None] = mapped_column(String(10))

    # 기타 처리 정보
    jung_chk_yn: Mapped[str | None] = mapped_column(String(2))
    mall_order_seq: Mapped[str | None] = mapped_column(String(20))
    mall_order_id: Mapped[str | None] = mapped_column(String(100))
    etc_field3: Mapped[str | None] = mapped_column(Text)
    ord_field2: Mapped[str | None] = mapped_column(String(10))
    copy_idx: Mapped[str | None] = mapped_column(String(50))

    # 분류 정보
    class_cd1: Mapped[str | None] = mapped_column(String(50))
    class_cd2: Mapped[str | None] = mapped_column(String(50))
    class_cd3: Mapped[str | None] = mapped_column(String(50))
    class_cd4: Mapped[str | None] = mapped_column(String(50))
    brand_nm: Mapped[str | None] = mapped_column(String(100))

    # 배송 정보
    delivery_id: Mapped[str | None] = mapped_column(String(50))
    invoice_no: Mapped[str | None] = mapped_column(String(100))
    inv_send_msg: Mapped[str | None] = mapped_column(Text)

    # 사은품 및 기타
    free_gift: Mapped[str | None] = mapped_column(Text)
    fld_dsp: Mapped[str | None] = mapped_column(Text)
    acnt_regs_srno: Mapped[int | None] = mapped_column(Integer)

    # 자사몰 확장 필드 (1~14)
    order_etc_1: Mapped[str | None] = mapped_column(Text)
    order_etc_2: Mapped[str | None] = mapped_column(Text)
    order_etc_3: Mapped[str | None] = mapped_column(Text)
    order_etc_4: Mapped[str | None] = mapped_column(Text)
    order_etc_5: Mapped[str | None] = mapped_column(Text)
    order_etc_6: Mapped[str | None] = mapped_column(Text)
    order_etc_7: Mapped[str | None] = mapped_column(Text)
    order_etc_8: Mapped[str | None] = mapped_column(Text)
    order_etc_9: Mapped[str | None] = mapped_column(Text)
    order_etc_10: Mapped[str | None] = mapped_column(Text)
    order_etc_11: Mapped[str | None] = mapped_column(Text)
    order_etc_12: Mapped[str | None] = mapped_column(Text)
    order_etc_13: Mapped[str | None] = mapped_column(Text)
    order_etc_14: Mapped[str | None] = mapped_column(Text)

    def to_dict(self, exclude_fields: set[str] = None) -> dict[str, Any]:
        exclude_fields = exclude_fields or set()
        dict_model: dict[str, Any] = {}
        
        for column in self.__table__.columns:
            if column.name in exclude_fields:
                continue
                
            # server_default가 있고 값이 None이면 제외
            value = getattr(self, column.name, None)
            if value is None and column.server_default is not None:
                continue
                
            # datetime과 Decimal 타입 처리
            if isinstance(value, Decimal):
                dict_model[column.name] = float(value) if value else None
            else:
                dict_model[column.name] = value
                
        return dict_model
