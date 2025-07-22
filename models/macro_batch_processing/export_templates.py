from models.base_model import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Boolean, Integer, String, Text, text


class ExportTemplates(Base):
    __tablename__ = "export_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    template_code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    template_name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text)
    is_aggregated: Mapped[bool] = mapped_column(Boolean, default=False)
    group_by_fields: Mapped[list[str]] = mapped_column()
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)