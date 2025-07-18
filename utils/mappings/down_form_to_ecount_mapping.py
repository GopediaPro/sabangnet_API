"""
DownFormOrder를 EcountSale로 매핑하는 매퍼
"""
from typing import Optional
from datetime import datetime
from utils.logs.sabangnet_logger import get_logger
from models.down_form_orders.down_form_order import BaseDownFormOrder
from schemas.ecount.sale_schemas import EcountSaleDto


logger = get_logger(__name__)


class DownFormOrderToEcountMapper:
    """DownFormOrder를 EcountSale로 매핑하는 클래스"""
    
    def __init__(self):
        pass
    
    def map_to_ecount_sale_dto(self, order: BaseDownFormOrder, com_code: str, user_id: str) -> EcountSaleDto:
        """DownFormOrder를 EcountSaleDto로 매핑합니다."""
        try:
            # 고객정보 조합 (REMARKS)
            remarks = self._build_remarks(order)
            
            # 주소 조합 (u_txt1)
            address = self._build_address(order)
            
            # 날짜 변환
            io_date = self._format_date(order.order_date)
            
            return EcountSaleDto(
                com_code=com_code,
                user_id=user_id,
                
                # 기본 매핑
                upload_ser_no=order.seq,
                io_date=io_date,
                cust=order.delivery_id,  # 거래처코드 = 택배사코드
                cust_des="",  # 거래처명은 비워둠
                emp_cd=user_id,  # 담당자 = 요청 사용자
                wh_cd=order.location_nm or "",  # 출하창고 = Location
                
                # 품목 정보
                prod_cd=order.product_id or "",
                prod_des=order.product_name or "",
                size_des=order.order_id,  # 규격(주문번호)
                qty=float(order.sale_cnt) if order.sale_cnt else 0,
                price=0,  # 단가는 계산 필요
                supply_amt=float(order.pay_cost) if order.pay_cost else 0,
                vat_amt=0,  # 부가세는 계산 필요
                remarks=remarks,
                
                # 적요 필드들
                p_remarks1=order.invoice_no or "",  # 송장번호
                p_remarks2=order.delv_msg or "",  # 배송메시지
                p_remarks3=order.mall_product_id or "",  # 상품번호
                
                # 금액 필드들
                p_amt1=float(order.expected_payout) if order.expected_payout else 0,  # 정산예정금액
                p_amt2=float(order.service_fee) if order.service_fee else 0,  # 서비스이용료
                
                # 기타 필드들
                item_des=order.delivery_class or "",  # 운임비타입
                temp_column_id1=order.sku_no or "",  # SKU번호
                
                # 연락처 정보
                u_memo1="",  # E-MAIL (없음)
                u_memo2="",  # FAX (없음) 
                u_memo3=order.receive_cel or "",  # 연락처
                u_txt1=address,  # 주소
                
                # 메타 정보
                is_test=True  # 기본값으로 테스트 모드
            )
            
        except Exception as e:
            logger.error(f"매핑 중 오류 발생: {e}, order_id: {order.idx}")
            raise
    
    def _build_remarks(self, order: BaseDownFormOrder) -> str:
        """고객정보를 조합하여 REMARKS 필드를 생성합니다."""
        try:
            # [fld_dsp](receive_name/idx/receive_cel/receive_addr/order_etc_7/mall_order_id)
            fld_dsp = order.fld_dsp or "사이트명"
            receive_name = order.receive_name or ""
            idx = order.idx or ""
            receive_cel = order.receive_cel or ""
            receive_addr = order.receive_addr or ""
            order_etc_7 = order.order_etc_7 or ""
            mall_order_id = order.mall_order_id or ""
            
            # 형식: [사이트명](수취인명/주문번호/연락처/주소/관리코드/장바구니번호)
            remarks = f"[{fld_dsp}]({receive_name}/{idx}/{receive_cel}/{receive_addr}/{order_etc_7}/{mall_order_id})"
            
            # 최대 길이 제한 (200자)
            if len(remarks) > 200:
                remarks = remarks[:197] + "..."
            
            return remarks
            
        except Exception as e:
            logger.warning(f"REMARKS 생성 중 오류: {e}")
            return f"[{order.fld_dsp or ''}]({order.receive_name or ''}/{order.idx or ''})"
    
    def _build_address(self, order: BaseDownFormOrder) -> str:
        """주소 정보를 조합합니다."""
        try:
            address_parts = []
            
            if order.receive_zipcode:
                address_parts.append(f"({order.receive_zipcode})")
            
            if order.receive_addr:
                address_parts.append(order.receive_addr)
            
            address = " ".join(address_parts)
            
            # 최대 길이 제한
            if len(address) > 2000:
                address = address[:1997] + "..."
            
            return address
            
        except Exception as e:
            logger.warning(f"주소 생성 중 오류: {e}")
            return order.receive_addr or ""
    
    def _format_date(self, date_value) -> Optional[str]:
        """날짜를 YYYYMMDD 형식으로 변환합니다."""
        try:
            if not date_value:
                return datetime.now().strftime("%Y%m%d")
            
            if isinstance(date_value, datetime):
                return date_value.strftime("%Y%m%d")
            
            if isinstance(date_value, str):
                # 이미 YYYYMMDD 형식인지 확인
                if len(date_value) == 8 and date_value.isdigit():
                    return date_value
                
                # 다른 형식이면 파싱 시도
                try:
                    parsed_date = datetime.strptime(date_value[:10], "%Y-%m-%d")
                    return parsed_date.strftime("%Y%m%d")
                except:
                    pass
            
            # 변환 실패 시 현재 날짜 사용
            return datetime.now().strftime("%Y%m%d")
            
        except Exception as e:
            logger.warning(f"날짜 변환 중 오류: {e}")
            return datetime.now().strftime("%Y%m%d")
    
    def calculate_price_and_vat(self, sale_dto: EcountSaleDto) -> EcountSaleDto:
        """단가와 부가세를 계산합니다."""
        try:
            if sale_dto.qty and sale_dto.qty > 0 and sale_dto.supply_amt:
                # 단가 = 공급가액 / 수량
                sale_dto.price = round(sale_dto.supply_amt / sale_dto.qty, 2)
                
                # 부가세 = 공급가액 * 0.1
                sale_dto.vat_amt = round(sale_dto.supply_amt * 0.1, 2)
            
            return sale_dto
            
        except Exception as e:
            logger.warning(f"가격 계산 중 오류: {e}")
            return sale_dto
    
    def validate_mapped_data(self, sale_dto: EcountSaleDto) -> list[str]:
        """매핑된 데이터를 검증하고 오류 목록을 반환합니다."""
        errors = []
        
        # 필수 필드 검증 (간단하게)
        if not sale_dto.prod_cd:
            errors.append("품목코드가 없습니다.")
        
        if not sale_dto.qty or sale_dto.qty <= 0:
            errors.append("수량이 유효하지 않습니다.")
        
        if not sale_dto.wh_cd:
            errors.append("출하창고코드가 없습니다.")
        
        return errors
