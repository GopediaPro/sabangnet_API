from models.base_model import Base
from sqlalchemy import Column, BigInteger, String, TIMESTAMP

class MallFormMacro(Base):
    __tablename__ = "mall_form_macro"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    shop_code = Column(String(100))
    form_basic_erp = Column(String(50))
    form_basic_bundle = Column(String(50))
    form_star_erp = Column(String(50))
    form_star_bundle = Column(String(50))
    macro_erp = Column(String(50))
    macrp_bundle = Column(String(50))
    created_at = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP")
    updated_at = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP") 