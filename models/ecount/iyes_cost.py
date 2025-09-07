from decimal import Decimal
from datetime import datetime
from models.base_model import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Integer, String, Text, Numeric, DateTime, UniqueConstraint
from schemas.receive_orders.receive_orders_dto import ReceiveOrdersDto


class EcountIyesCost(Base):
    """
    이카운트 IYES 단가 테이블의 ORM 매핑 모델
    """

    __tablename__ = "ecount_iyes_cost"

    id = Column(Integer, primary_key=True, index=True)
    product_nm = Column(String(255), nullable=True, comment="제품명")
    cost = Column(Integer, nullable=True, comment="원가(VAT 포함)")
    cost_10_vat = Column(Integer, nullable=True, comment="원가(VAT 10%)")
    cost_20_vat = Column(Integer, nullable=True, comment="원가(VAT 20%)")