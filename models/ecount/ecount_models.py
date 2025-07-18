"""
이카운트 관련 DB 모델 (향후 확장용)
"""
from sqlalchemy import Column, String, DateTime, Text, Integer, Boolean, Numeric
from sqlalchemy.dialects.postgresql import UUID
from models.base_model import Base
from datetime import datetime
import uuid


class EcountSale(Base):
    """이카운트 판매 데이터"""
    __tablename__ = "ecount_sale"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    com_code = Column(String(6), nullable=False, comment="회사코드")
    user_id = Column(String(30), nullable=False, comment="사용자ID")
    
    # 요청 정보
    upload_ser_no = Column(Integer, comment="순번")
    io_date = Column(String(8), comment="판매일자")
    cust = Column(String(30), comment="거래처코드")
    cust_des = Column(String(50), comment="거래처명")
    wh_cd = Column(String(5), nullable=False, comment="출하창고코드")
    prod_cd = Column(String(20), nullable=False, comment="품목코드")
    prod_des = Column(String(100), comment="품목명")
    qty = Column(Numeric(28, 10), nullable=False, comment="수량")
    price = Column(Numeric(28, 10), comment="단가")
    supply_amt = Column(Numeric(28, 4), comment="공급가액")
    vat_amt = Column(Numeric(28, 4), comment="부가세")
    remarks = Column(String(200), comment="적요")
    
    # API 응답 정보
    is_success = Column(Boolean, default=False, comment="성공여부")
    slip_no = Column(String(30), comment="판매번호(ERP)")
    trace_id = Column(String(100), comment="로그확인용 일련번호")
    error_message = Column(Text, comment="오류메시지")
    
    # 메타 정보
    is_test = Column(Boolean, default=True, comment="테스트 여부")
    created_at = Column(DateTime, default=datetime.utcnow, comment="생성일시")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="수정일시")


class EcountAuthSession(Base):
    """이카운트 인증 세션"""
    __tablename__ = "ecount_auth_session"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    com_code = Column(String(6), nullable=False, comment="회사코드")
    user_id = Column(String(30), nullable=False, comment="사용자ID")
    zone = Column(String(2), nullable=False, comment="Zone 정보")
    domain = Column(String(30), nullable=False, comment="도메인 정보")
    session_id = Column(String(100), nullable=False, comment="세션ID")
    
    # 세션 관리
    is_active = Column(Boolean, default=True, comment="활성 여부")
    is_test = Column(Boolean, default=True, comment="테스트 여부")
    expires_at = Column(DateTime, comment="만료일시")
    created_at = Column(DateTime, default=datetime.utcnow, comment="생성일시")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="수정일시")


class EcountApiLog(Base):
    """이카운트 API 호출 로그"""
    __tablename__ = "ecount_api_log"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    com_code = Column(String(6), nullable=False, comment="회사코드")
    user_id = Column(String(30), nullable=False, comment="사용자ID")
    api_type = Column(String(20), nullable=False, comment="API 유형 (zone, login, sale)")
    api_url = Column(String(500), nullable=False, comment="API URL")
    
    # 요청/응답 정보
    request_method = Column(String(10), default="POST", comment="요청 메소드")
    request_headers = Column(Text, comment="요청 헤더")
    request_body = Column(Text, comment="요청 본문")
    response_status = Column(Integer, comment="응답 상태코드")
    response_headers = Column(Text, comment="응답 헤더")
    response_body = Column(Text, comment="응답 본문")
    
    # 성능 정보
    response_time_ms = Column(Integer, comment="응답시간(밀리초)")
    is_success = Column(Boolean, default=False, comment="성공여부")
    error_message = Column(Text, comment="오류메시지")
    
    # 메타 정보
    is_test = Column(Boolean, default=True, comment="테스트 여부")
    created_at = Column(DateTime, default=datetime.utcnow, comment="생성일시")


class EcountConfig(Base):
    """이카운트 설정"""
    __tablename__ = "ecount_config"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    config_key = Column(String(100), nullable=False, unique=True, comment="설정 키")
    config_value = Column(Text, comment="설정 값")
    description = Column(String(500), comment="설명")
    
    # 메타 정보
    is_active = Column(Boolean, default=True, comment="활성 여부")
    created_at = Column(DateTime, default=datetime.utcnow, comment="생성일시")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="수정일시")
