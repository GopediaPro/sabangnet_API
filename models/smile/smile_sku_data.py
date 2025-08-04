from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column
from models.base_model import Base


class SmileSkuData(Base):
    """
    스마일배송 SKU 데이터 모델
    SKU 정보 및 모델명 매핑 데이터
    """
    __tablename__ = "smile_sku_data"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # SKU 데이터 필드
    sku_number: Mapped[str] = mapped_column(String(100), nullable=True, comment="SKU번호")
    model_name: Mapped[str] = mapped_column(String(200), nullable=True, comment="모델명")
    sku_name: Mapped[str] = mapped_column(String(200), nullable=True, comment="SKU명")
    comment: Mapped[str] = mapped_column(Text, nullable=True, comment="comment")

    def __repr__(self):
        return f"<SmileSkuData(id={self.id}, sku_number='{self.sku_number}', model_name='{self.model_name}')>" 