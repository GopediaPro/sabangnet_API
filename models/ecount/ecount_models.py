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
    io_date = Column(String(8), comment="판매일자")
    upload_ser_no = Column(Integer, comment="순번")
    cust = Column(String(30), comment="거래처코드")
    cust_des = Column(String(50), comment="거래처명")
    emp_cd = Column(String(30), nullable=False, comment="담당자") # 담당자 코드 ex; okokmart5
    wh_cd = Column(Integer, nullable=False, comment="출하창고")
    io_type = Column(String(10), nullable=False, comment="거래유형")
    exchange_type = Column(String(5), nullable=True, comment="통화")
    exchange_rate = Column(Numeric(18, 4), nullable=True, comment="환율")
    u_memo1 = Column(String(100), comment="E-MAIL")
    u_memo2 = Column(String(100), comment="FAX")
    u_memo3 = Column(String(100), comment="연락처")
    u_txt1 = Column(String(100), comment="주소")
    u_memo4 = Column(String(100), comment="매장판매 결제구분(입금/현금/카드)")
    u_memo5 = Column(String(100), comment="매장판매 거래구분(매장판매/매장구매)")
    prod_cd = Column(String(20), nullable=False, comment="품목코드")
    prod_des = Column(String(100), comment="품목명")
    qty = Column(Numeric(28, 0), nullable=False, comment="수량")
    price = Column(Numeric(28, 10), comment="단가")
    supply_amt_f = Column(Numeric(28, 10), comment="외화금액")
    supply_amt = Column(Numeric(28, 4), comment="공급가액")
    vat_amt = Column(Numeric(28, 4), comment="부가세")
    remarks = Column(Text, comment="고객정보(이름/주문번호/연락처/주소/관리코드/장바구니번호")
    p_remarks2 = Column(String(100), comment="배송메시지")
    p_remarks1 = Column(String(100), comment="송장번호")
    p_remarks3 = Column(String(100), comment="상품번호")
    size_des = Column(String(100), comment="주문번호")
    p_amt1 = Column(Numeric(28, 10), comment="정산예정금액")
    p_amt2 = Column(Numeric(28, 10), comment="서비스이용료")
    item_cd = Column(String(14), comment="운임비타입")
    
    # API 응답 정보
    is_success = Column(Boolean, default=False, comment="성공여부")
    slip_nos = Column(String(30), comment="판매번호(ERP)")
    trace_id = Column(String(100), comment="로그확인용 일련번호")
    error_message = Column(Text, comment="오류메시지")
    
    # 메타 정보
    is_test = Column(Boolean, default=True, comment="테스트 여부")
    work_status = Column(String(255), comment="작업상태") # ERP 업로드 전, ERP 업로드 완료
    batch_id = Column(String(255), comment="배치ID")
    template_code = Column(String(255), comment="템플릿코드")  # okmart_erp_sale_ok , okmart_erp_sale_iyes, iyes_erp_sale_iyes

class EcountPurchase(Base):
    """이카운트 구매 데이터"""
    __tablename__ = "ecount_purchase"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    com_code = Column(String(6), nullable=False, comment="회사코드")
    user_id = Column(String(30), nullable=False, comment="사용자ID")
    emp_cd = Column(String(30), nullable=False, comment="담당자") # 담당자 코드 ex; okokmart5
    
    # 요청 정보
    io_date = Column(String(8), comment="구매일자")
    upload_ser_no = Column(Integer, comment="순번")
    cust = Column(String(30), comment="거래처코드")
    cust_des = Column(String(50), comment="거래처명")
    wh_cd = Column(Integer, nullable=False, comment="입고창고")
    io_type = Column(String(10), nullable=False, comment="거래유형")
    exchange_type = Column(String(5), nullable=True, comment="통화")
    exchange_rate = Column(Numeric(18, 4), nullable=True, comment="환율")
    u_memo1 = Column(String(100), comment="E-MAIL")
    u_memo2 = Column(String(100), comment="FAX")
    u_memo3 = Column(String(100), comment="연락처")
    u_txt1 = Column(String(100), comment="주소")
    prod_cd = Column(String(20), nullable=False, comment="품목코드")
    prod_des = Column(String(100), comment="품목명")
    size_des = Column(String(100), comment="규격")
    qty = Column(Numeric(28, 0), nullable=False, comment="수량")
    price = Column(Numeric(28, 10), comment="단가")
    supply_amt_f = Column(Numeric(28, 10), comment="외화금액")
    supply_amt = Column(Numeric(28, 4), comment="공급가액")
    vat_amt = Column(Numeric(28, 4), comment="부가세")
    remarks = Column(Text, comment="적요")
    
    # API 응답 정보
    is_success = Column(Boolean, default=False, comment="성공여부")
    slip_nos = Column(String(30), comment="구매번호(ERP)")
    trace_id = Column(String(100), comment="로그확인용 일련번호")
    error_message = Column(Text, comment="오류메시지")
    
    # 메타 정보
    is_test = Column(Boolean, default=True, comment="테스트 여부")
    work_status = Column(String(255), comment="작업상태") # ERP 업로드 전, ERP 업로드 완료
    batch_id = Column(String(255), comment="배치ID")
    template_code = Column(String(255), comment="템플릿코드")  # iyes_erp_purchase_iyes


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


class EcountConfig(Base):
    """이카운트 설정"""
    __tablename__ = "ecount_config"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    config_key = Column(String(100), nullable=False, unique=True, comment="설정 키")
    config_value = Column(Text, comment="설정 값")
    description = Column(String(500), comment="설명")
    
    # 메타 정보
    is_active = Column(Boolean, default=True, comment="활성 여부")
