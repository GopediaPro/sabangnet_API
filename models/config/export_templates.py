from models.base_model import Base
from sqlalchemy import Column, Integer, String, Boolean, Text, ARRAY, TIMESTAMP

class ExportTemplates(Base):
    __tablename__ = "export_templates"
    id = Column(Integer, primary_key=True, autoincrement=True)
    template_code = Column(String(50), nullable=False, unique=True)
    template_name = Column(String(100), nullable=False, comment="표시용 이름")
    site_type = Column(String(20), nullable=True, comment="template 구분. 구분자 -- , -- [G마켓,옥션], [기본양식], [브랜디]")
    usage_type = Column(String(20), nullable=True, comment="template 구분. 구분자 -- , -- ERP용, 합포장용")
    is_star = Column(Boolean, server_default="false", comment="스타배송 여부")
    description = Column(Text)
    is_aggregated = Column(Boolean, server_default="false")
    group_by_fields = Column(ARRAY(Text))
    is_active = Column(Boolean, server_default="true")
    created_at = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP")
    updated_at = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP") 