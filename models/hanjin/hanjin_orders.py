"""
한진택배 주문 관련 DB 모델
"""
from sqlalchemy import Column, String, DateTime, Text, Integer, func
from sqlalchemy.dialects.postgresql import JSON
from models.base_model import Base


class HanjinOrder(Base):
    """한진택배 주문 모델"""
    __tablename__ = "hanjin_orders"

    # 기본 정보
    id = Column(Integer, primary_key=True, index=True)
    cust_edi_cd = Column(String(50), nullable=True, comment="EDI코드")
    cust_ord_no = Column(String(100), nullable=True, unique=True, comment="주문번호")
    wbl_no = Column(String(50), nullable=True, comment="운송장번호")
    svc_cat_cd = Column(String(1), nullable=True, comment="배송구분(S:출고, F:포커스, E:직택배, R:반품)")
    contract_no = Column(String(50), nullable=True, comment="계약번호")
    pickup_ask_dt = Column(String(8), nullable=True, comment="주문 전송일(YYYYMMDD)")
    
    # 송하인 정보
    sndr_zip = Column(String(10), nullable=True, comment="송하인 우편번호")
    sndr_base_addr = Column(String(500), nullable=True, comment="송하인 주소1")
    sndr_dtl_addr = Column(String(500), nullable=True, comment="송하인 주소2")
    sndr_nm = Column(String(100), nullable=True, comment="송하인명")
    sndr_tel_no = Column(String(20), nullable=True, comment="송하인 전화번호")
    sndr_mobile_no = Column(String(20), nullable=True, comment="송하인 핸드폰번호")
    sndr_ask_content = Column(Text, nullable=True, comment="송하인 배송메시지")
    sndr_ref_content = Column(String(100), nullable=True, comment="송하인 담당자명")
    
    # 수하인 정보
    rcvr_zip = Column(String(10), nullable=True, comment="수하인 우편번호")
    rcvr_base_addr = Column(String(500), nullable=True, comment="수하인 주소1")
    rcvr_dtl_addr = Column(String(500), nullable=True, comment="수하인 주소2")
    rcvr_nm = Column(String(100), nullable=True, comment="수하인명")
    rcvr_tel_no = Column(String(20), nullable=True, comment="수하인 전화번호")
    rcvr_mobile_no = Column(String(20), nullable=True, comment="수하인 핸드폰번호")
    rcvr_ask_content = Column(Text, nullable=True, comment="수하인 배송메시지")
    rcvr_ref_content = Column(String(100), nullable=True, comment="수하인 담당자명")
    
    # 상품 및 배송 정보
    commodity_nm = Column(String(200), nullable=True, comment="상품명")
    pay_typ_cd = Column(String(2), nullable=True, comment="지불조건 CD(발지신용), CT(착지신용), PP(선불), CC(착불)")
    box_typ_cd = Column(String(1), nullable=True, comment="박스타입(S,A,B,C,D,E)")
    
    # 메모 필드들
    print_memo1 = Column(String(500), nullable=True, comment="메모1")
    print_memo2 = Column(String(500), nullable=True, comment="메모2")
    print_memo3 = Column(String(500), nullable=True, comment="메모3")
    print_memo4 = Column(String(500), nullable=True, comment="메모4")
    
    # 상품 리스트 (JSON 형태로 저장)
    commodity_list = Column(JSON, nullable=True, comment="상품리스트")
    
    # 시스템 필드
    status = Column(String(20), default="pending", comment="주문상태")
    
    def __repr__(self):
        return f"<HanjinOrder(id={self.id}, cust_ord_no='{self.cust_ord_no}', wbl_no='{self.wbl_no}')>"
