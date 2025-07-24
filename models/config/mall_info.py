from models.base_model import Base
from sqlalchemy import Column, BigInteger, String, TIMESTAMP

class MallInfo(Base):
    __tablename__ = "mall_info"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    mall_id = Column(String(100))
    shop_code = Column(String(100))
    created_at = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP")
    updated_at = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP") 