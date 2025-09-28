from models.base_model import Base
from sqlalchemy import Column, BigInteger, String, TIMESTAMP

class MallInfo(Base):
    __tablename__ = "mall_info"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    mall_id = Column(String(100)) # 쇼핑몰 이름
    shop_code = Column(String(100)) # 쇼핑몰 코드
    mall_price_function = Column(String(255)) # 쇼핑몰 판매가 함수
    gubun = Column(String(255)) # 쇼핑몰 구분 (마스터,전문몰,1+1)
    delivery_type = Column(String(255)) # 배송 타입 (무료배송, 유료배송)
    created_at = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP")
    updated_at = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP") 