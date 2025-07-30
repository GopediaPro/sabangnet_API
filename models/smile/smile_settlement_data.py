from datetime import datetime
from sqlalchemy import String, Date, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from models.base_model import Base


class SmileSettlementData(Base):
    """
    스마일배송 정산 데이터 모델
    정산 시스템에서 가져온 정산 데이터
    """
    __tablename__ = "smile_settlement_data"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # 정산 데이터 필드
    order_number: Mapped[str] = mapped_column(String(100), nullable=True, comment="주문번호")
    product_number: Mapped[str] = mapped_column(String(100), nullable=True, comment="상품번호")
    cart_number: Mapped[str] = mapped_column(String(100), nullable=True, comment="장바구니번호")
    product_name: Mapped[str] = mapped_column(String(200), nullable=True, comment="상품명")
    buyer_name: Mapped[str] = mapped_column(String(100), nullable=True, comment="구매자명")
    payment_confirmation_date: Mapped[datetime] = mapped_column(Date, nullable=True, comment="입금확인일")
    delivery_completion_date: Mapped[datetime] = mapped_column(Date, nullable=True, comment="배송완료일")
    early_settlement_date: Mapped[datetime] = mapped_column(Date, nullable=True, comment="조기정산일자")
    settlement_type: Mapped[str] = mapped_column(String(50), nullable=True, comment="구분")
    sales_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=True, comment="판매금액")
    service_fee: Mapped[float] = mapped_column(Numeric(10, 2), nullable=True, comment="서비스이용료")
    settlement_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=True, comment="정산금액")
    transfer_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=True, comment="송금대상액")
    payment_date: Mapped[datetime] = mapped_column(Date, nullable=True, comment="결제일")
    shipping_date: Mapped[datetime] = mapped_column(Date, nullable=True, comment="발송일")
    refund_date: Mapped[datetime] = mapped_column(Date, nullable=True, comment="환불일")
    site: Mapped[str] = mapped_column(String(50), nullable=True, comment="사이트")

    def __repr__(self):
        return f"<SmileSettlementData(id={self.id}, order_number='{self.order_number}', site='{self.site}')>" 