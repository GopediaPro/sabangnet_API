from models.base_model import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Boolean, Integer, String, Text, text


class TemplateColumnMappings(Base):
    """
    템플릿 컬럼 매핑 테이블(template_column_mappings)의 ORM 매핑 모델
    """

    __tablename__ = "template_column_mappings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    template_id: Mapped[int] = mapped_column(Integer)
    column_order: Mapped[int] = mapped_column(Integer, nullable=False)
    target_column: Mapped[str] = mapped_column(String(100), nullable=False)
    source_field: Mapped[str] = mapped_column(String(100))
    field_type: Mapped[str] = mapped_column(String(20), nullable=False)
    transform_config: Mapped[dict] = mapped_column(JSONB, default={}, server_default=text("'{}'::jsonb"))
    aggregation_type: Mapped[str] = mapped_column(String(20), default="none")
    description: Mapped[str] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)