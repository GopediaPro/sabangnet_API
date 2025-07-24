from models.base_model import Base
from sqlalchemy import Column, Integer, String, Boolean, Text, ARRAY, TIMESTAMP

class ExportTemplates(Base):
    __tablename__ = "export_templates"
    id = Column(Integer, primary_key=True, autoincrement=True)
    template_code = Column(String(50), nullable=False, unique=True)
    template_name = Column(String(100), nullable=False)
    description = Column(Text)
    is_aggregated = Column(Boolean, server_default="false")
    group_by_fields = Column(ARRAY(Text))
    is_active = Column(Boolean, server_default="true")
    created_at = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP")
    updated_at = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP") 