from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, Text, Numeric
from decimal import Decimal
from models.base_model import Base

class VlookupDatas(Base):
    """VLOOKUP 데이터 테이블 모델"""
    __tablename__ = "vlookup_datas"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    mall_product_id: Mapped[str | None] = mapped_column(Text)
    delv_cost: Mapped[Decimal | None] = mapped_column(Numeric(30, 2))

    