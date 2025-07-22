from models.base_model import Base
from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, JSON, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import JSONB

class TemplateColumnMappings(Base):
    __tablename__ = "template_column_mappings"
    id = Column(Integer, primary_key=True, autoincrement=True)
    template_id = Column(Integer, ForeignKey("export_templates.id", ondelete="CASCADE"))
    column_order = Column(Integer, nullable=False)
    target_column = Column(String(100), nullable=False)
    source_field = Column(String(100))
    field_type = Column(String(20), nullable=False)
    transform_config = Column(JSONB, server_default='{}')
    aggregation_type = Column(String(20), server_default="none")
    description = Column(Text)
    is_active = Column(Boolean, server_default="true")

    __table_args__ = (
        UniqueConstraint('template_id', 'column_order', name='template_column_mappings_template_id_column_order_key'),
        Index('idx_template_column_mappings_order', 'template_id', 'column_order'),
        Index('idx_template_column_mappings_template_id', 'template_id'),
    ) 