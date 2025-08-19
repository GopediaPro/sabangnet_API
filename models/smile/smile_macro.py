from datetime import datetime
from sqlalchemy import String, Date, Numeric, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column
from models.base_model import Base


class SmileMacro(Base):
    """
    스마일배송 매크로 데이터 모델
    """
    __tablename__ = "smile_macro"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # 스마일배송 매크로 데이터 필드
    fld_dsp: Mapped[str] = mapped_column(String(100), comment="아이디*")
    expected_payout: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True, comment="정산예정금??")
    service_fee: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True, comment="서비스 이용료")
    mall_order_id: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="장바구니번호(결제번호)")
    pay_cost: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True, comment="금액[배송비미포함]")
    delv_cost: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True, comment="배송비 금액")
    # 구매결정일자 - source_field 없음
    mall_product_id: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="상품번호*")
    order_id: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="주문번호*")
    chat_1: Mapped[str | None] = mapped_column(String(200), nullable=True, comment="주문옵션")
    product_name: Mapped[str | None] = mapped_column(String(500), nullable=True, comment="상품명")
    item_name: Mapped[str | None] = mapped_column(String(500), nullable=True, comment="제품명")
    sale_cnt: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="수량")
    # 추가구성 - source_field 없음
    # 사은품 - source_field 없음
    sale_cost: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True, comment="판매금액")
    mall_user_id: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="구매자ID")
    user_name: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="구매자명")
    receive_name: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="수령인명")
    delivery_method_str: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="배송비")
    receive_cel: Mapped[str | None] = mapped_column(String(20), nullable=True, comment="수령인 휴대폰")
    receive_tel: Mapped[str | None] = mapped_column(String(20), nullable=True, comment="수령인 전화번호")
    receive_addr: Mapped[str | None] = mapped_column(Text, nullable=True, comment="주소")
    receive_zipcode: Mapped[str | None] = mapped_column(String(10), nullable=True, comment="우편번호")
    delv_msg: Mapped[str | None] = mapped_column(Text, nullable=True, comment="배송시 요구사항")
    # (옥션)복수구매할인 - source_field 없음
    # (옥션)우수회원할인 - source_field 없음
    sku1_num: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="SKU1번호")
    sku1_cnt: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="SKU1수량")
    sku2_num: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="SKU2번호")
    sku2_cnt: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="SKU2수량")
    sku_num: Mapped[str | None] = mapped_column(String(200), nullable=True, comment="SKU번호 및 수량")
    pay_dt: Mapped[datetime | None] = mapped_column(Date, nullable=True, comment="결제완료일")
    user_tel: Mapped[str | None] = mapped_column(String(20), nullable=True, comment="구매자 전화번호")
    user_cel: Mapped[str | None] = mapped_column(String(20), nullable=True, comment="구매자 휴대폰")
    buy_coupon: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True, comment="구매쿠폰적용금액")
    # 발송예정일 - source_field 없음
    # 발송일자 - source_field 없음
    # 배송구분 - source_field 없음
    delv_id: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="배송번호")
    delv_status: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="배송상태")
    # 배송완료일자 - source_field 없음
    # 배송지연사유 - source_field 없음
    # 배송점포 - source_field 없음
    # 상품미수령상세사유 - source_field 없음
    # 상품미수령신고사유 - source_field 없음
    # 상품미수령신고일자 - source_field 없음
    # 상품미수령이의제기일자 - source_field 없음
    # 상품미수령철회요청일자 - source_field 없음
    # 송장번호(방문수령인증키) - source_field 없음
    # 일시불할인 - source_field 없음
    # 재배송일 - source_field 없음
    # 재배송지 우편번호 - source_field 없음
    # 재배송지 운송장번호 - source_field 없음
    # 재배송지 주소 - source_field 없음
    # 재배송택배사명 - source_field 없음
    # 정산완료일 - source_field 없음
    order_dt: Mapped[datetime | None] = mapped_column(Date, nullable=True, comment="주문일자(결제확인전)")
    order_method: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="주문종류")
    # 주문확인일자 - source_field 없음
    delv_method_id: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="택배사명(발송방법)")
    # 판매단가 - source_field 없음 (sale_cost와 중복)
    sale_method: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="판매방식")
    order_etc_7: Mapped[str | None] = mapped_column(String(200), nullable=True, comment="판매자 관리코드")
    # 판매자 상세관리코드 - source_field 없음
    # 판매자북캐시적립 - source_field 없음
    sale_coupon: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True, comment="판매자쿠폰할인")
    # 판매자포인트적립 - source_field 없음
    

