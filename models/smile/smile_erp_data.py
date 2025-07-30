from datetime import datetime
from sqlalchemy import String, Date
from sqlalchemy.orm import Mapped, mapped_column
from models.base_model import Base


class SmileErpData(Base):
    """
    스마일배송 ERP 데이터 모델
    ERP 시스템에서 가져온 주문 데이터
    """
    __tablename__ = "smile_erp_data"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # ERP 데이터 필드
    date: Mapped[datetime] = mapped_column(Date, nullable=True, comment="날짜")
    site: Mapped[str] = mapped_column(String(50), nullable=True, comment="사이트")
    customer_name: Mapped[str] = mapped_column(String(100), nullable=True, comment="고객성함")
    order_number: Mapped[str] = mapped_column(String(100), nullable=True, comment="주문번호")
    erp_code: Mapped[str] = mapped_column(String(100), nullable=True, comment="ERP")

    def __repr__(self):
        return f"<SmileErpData(id={self.id}, order_number='{self.order_number}', site='{self.site}')>" 