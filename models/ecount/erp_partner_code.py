from decimal import Decimal
from datetime import datetime
from models.base_model import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Integer, String, Text, Numeric, DateTime, UniqueConstraint, Column
from schemas.receive_orders.receive_orders_dto import ReceiveOrdersDto


class EcountErpPartnerCode(Base):
    """
    이카운트 ERP 파트너 코드 테이블의 ORM 매핑 모델
    """

    __tablename__ = "ecount_erp_partner_code"

    id = Column(Integer, primary_key=True, index=True)
    fld_dsp = Column(String(255), nullable=True, comment="업체명")
    partner_code = Column(String(255), nullable=True, comment="거래처 코드")
    product_nm = Column(String(255), nullable=True, comment="품목코드")
    wh_cd = Column(Integer, nullable=True, comment="창고코드")