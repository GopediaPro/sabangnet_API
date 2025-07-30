from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from models.base_model import Base


class HanjinPrintwbls(Base):
    """한진택배 운송장 출력 관련 DB 모델"""
    __tablename__ = "hanjin_printwbls"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="기본키")
    idx = Column(String(100), nullable=True, comment="주문번호")
    
    # AddressResult 스키마 기반 필드들
    msg_key = Column(String(100), nullable=True, comment="메세지KEY - 자료 매칭을 위한 고객사 고유키")
    result_code = Column(String(10), nullable=True, comment="결과코드")
    result_message = Column(String(200), nullable=True, comment="결과메세지")
    s_tml_nam = Column(String(100), nullable=True, comment="집하지 터미널명")
    s_tml_cod = Column(String(10), nullable=True, comment="집하지 터미널코드")
    zip_cod = Column(String(10), nullable=True, comment="정제된 우편번호")
    tml_nam = Column(String(100), nullable=True, comment="도착지 터미널명")
    tml_cod = Column(String(10), nullable=True, comment="도착지 터미널코드")
    cen_nam = Column(String(100), nullable=True, comment="도착지 집배점명")
    cen_cod = Column(String(10), nullable=True, comment="도착지 집배점코드")
    pd_tim = Column(String(10), nullable=True, comment="집배소요시간")
    dom_rgn = Column(String(10), nullable=True, comment="권역구분")
    hub_cod = Column(String(10), nullable=True, comment="허브코드")
    dom_mid = Column(String(10), nullable=True, comment="중분류코드")
    es_cod = Column(String(10), nullable=True, comment="배송사원분류코드")
    grp_rnk = Column(String(10), nullable=True, comment="소분류코드")
    es_nam = Column(String(100), nullable=True, comment="배송사원명")
    prt_add = Column(Text, nullable=True, comment="주소 출력정보")
    wbl_num = Column(String(50), nullable=True, comment="운송장번호")

    # 추가 필드
    snd_zip = Column(String(10), nullable=True, comment="출발지 우편번호")
    
    # 생성/수정 시간
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="생성일시")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="수정일시")
