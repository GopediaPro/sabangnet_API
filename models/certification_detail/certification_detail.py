from sqlalchemy import (
    String, Integer
)
from sqlalchemy.orm import Mapped, mapped_column

from models.base_model import Base


class CertificationDetail(Base):
    __tablename__ = "certification_detail"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    certification_field: Mapped[str] = mapped_column(String(50))
    certification_agency: Mapped[str | None] = mapped_column(String(50))
    certification_code: Mapped[str] = mapped_column(String(50))