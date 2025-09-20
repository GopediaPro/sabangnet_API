"""
Smile Data Builder
스마일배송 데이터 처리를 위한 빌더 패턴
"""

import pandas as pd
from typing import List, Optional, Dict, Any
from datetime import datetime
from models.smile.smile_erp_data import SmileErpData
from models.smile.smile_settlement_data import SmileSettlementData
from models.smile.smile_sku_data import SmileSkuData
from schemas.smile.smile_excel_import_dto import SmileDataProcessingErrorDto
from utils.logs.sabangnet_logger import get_logger

logger = get_logger(__name__)

class SmileDataBuilder:
    """스마일배송 데이터 빌더"""
    
    def __init__(self, site: str = None):
        self.errors = []
        self.processed_count = 0
        self.skipped_count = 0
        self.site = site
        logger.info(f"SmileDataBuilder 초기화 - site: '{site}' (type: {type(site)})")
    
    def build_erp_data_list(self, df: pd.DataFrame) -> List[SmileErpData]:
        """ERP 데이터 리스트를 빌드합니다."""
        return [
            self._build_erp_data(row, index)
            for index, row in df.iterrows()
            if self._validate_erp_row(row, index)
        ]
    
    def build_settlement_data_list(self, df: pd.DataFrame) -> List[SmileSettlementData]:
        """정산 데이터 리스트를 빌드합니다."""
        result = []
        for index, row in df.iterrows():
            if self._validate_settlement_row(row, index):
                settlement_data = self._build_settlement_data(row, index)
                if settlement_data is not None:  # None 값 필터링
                    result.append(settlement_data)
                else:
                    logger.warning(f"정산 데이터 행 {index}에서 None 반환됨")
        return result
    
    def build_sku_data_list(self, df: pd.DataFrame) -> List[SmileSkuData]:
        """SKU 데이터 리스트를 빌드합니다."""
        return [
            self._build_sku_data(row, index)
            for index, row in df.iterrows()
            if self._validate_sku_row(row, index)
        ]
    
    def _validate_erp_row(self, row: pd.Series, index: int) -> bool:
        """ERP 행 유효성 검사"""
        date_value = row.get('date') or row.get('날짜')
        if pd.isna(date_value):
            self.skipped_count += 1
            return False
        return True
    
    def _validate_settlement_row(self, row: pd.Series, index: int) -> bool:
        """정산 행 유효성 검사"""
        # 빈 행인지 확인
        if row.isna().all():
            return False
        
        # 최소한 하나의 의미있는 데이터가 있는지 확인
        meaningful_fields = ['order_number', '주문번호', 'product_number', '상품번호', 'product_name', '상품명', 'buyer_name', '구매자명']
        has_meaningful_data = any(pd.notna(row.get(field, '')) for field in meaningful_fields)
        
        # 건너뛰어진 행에 대한 로깅 (처음 20개만)
        if not has_meaningful_data and self.skipped_count < 20:
            logger.warning(f"정산 데이터 행 {index} 건너뛰어짐 - 의미있는 데이터 없음")
            logger.warning(f"  행 전체 데이터: {dict(row)}")
        
        # 유효한 행에 대한 로깅 (처음 5개만)
        if has_meaningful_data and self.processed_count < 5:
            logger.info(f"정산 데이터 행 {index} 유효함")
        
        if not has_meaningful_data:
            self.skipped_count += 1
        
        return has_meaningful_data
    
    def _validate_sku_row(self, row: pd.Series, index: int) -> bool:
        """SKU 행 유효성 검사"""
        required_fields = ['sku_number', 'SKU번호', 'model_name', '모델명']
        return any(pd.notna(row.get(field, '')) for field in required_fields)
    
    def _build_erp_data(self, row: pd.Series, index: int) -> Optional[SmileErpData]:
        """ERP 데이터 객체 빌드"""
        try:
            date_value = row.get('date') or row.get('날짜')
            date_obj = self._parse_date(date_value)
            
            erp_data = SmileErpData(
                date=date_obj,
                site=str(row.get('site', row.get('사이트', ''))),
                customer_name=str(row.get('customer_name', row.get('고객성함', ''))),
                order_number=str(row.get('order_number', row.get('주문번호', ''))),
                erp_code=str(row.get('erp_code', row.get('ERP', ''))) if pd.notna(row.get('erp_code', row.get('ERP'))) else None
            )
            self.processed_count += 1
            return erp_data
        except Exception as e:
            self._add_error(index, row, e, "ERP")
            return None
    
    def _build_settlement_data(self, row: pd.Series, index: int) -> Optional[SmileSettlementData]:
        """정산 데이터 객체 빌드"""
        try:
            # site는 외부에서 받은 값을 사용하거나, Excel 파일에서 가져온 값을 사용
            site_value = self.site if self.site else str(row.get('site', row.get('사이트', '')))
            logger.info(f"정산 데이터 빌드 - row {index}: site_value='{site_value}' (builder.site='{self.site}')")
            
            # 각 필드를 안전하게 파싱
            try:
                order_number = str(row.get('order_number', row.get('주문번호', '')))
            except:
                order_number = ''
            
            try:
                product_number = str(row.get('product_number', row.get('상품번호', '')))
            except:
                product_number = ''
            
            try:
                cart_number = str(row.get('cart_number', row.get('장바구니번호', '')))
            except:
                cart_number = ''
            
            try:
                product_name = str(row.get('product_name', row.get('상품명', '')))
            except:
                product_name = ''
            
            try:
                buyer_name = str(row.get('buyer_name', row.get('구매자명', '')))
            except:
                buyer_name = ''
            
            # 날짜 필드들을 안전하게 파싱
            try:
                payment_confirmation_date = self._parse_date(row.get('payment_confirmation_date', row.get('입금확인일')))
            except:
                payment_confirmation_date = None
            
            try:
                delivery_completion_date = self._parse_date(row.get('delivery_completion_date', row.get('배송완료일')))
            except:
                delivery_completion_date = None
            
            try:
                early_settlement_date = self._parse_date(row.get('early_settlement_date', row.get('조기정산일자')))
            except:
                early_settlement_date = None
            
            try:
                settlement_type = str(row.get('settlement_type', row.get('구분', ''))) if pd.notna(row.get('settlement_type', row.get('구분'))) else None
            except:
                settlement_type = None
            
            # 숫자 필드들을 안전하게 파싱
            try:
                sales_amount = self._parse_numeric(row.get('sales_amount', row.get('판매금액')))
            except:
                sales_amount = None
            
            try:
                service_fee = self._parse_numeric(row.get('service_fee', row.get('서비스이용료')))
            except:
                service_fee = None
            
            try:
                settlement_amount = self._parse_numeric(row.get('settlement_amount', row.get('정산금액')))
            except:
                settlement_amount = None
            
            try:
                transfer_amount = self._parse_numeric(row.get('transfer_amount', row.get('송금대상액')))
            except:
                transfer_amount = None
            
            # 날짜 필드들을 안전하게 파싱
            try:
                payment_date = self._parse_date(row.get('payment_date', row.get('결제일')))
            except:
                payment_date = None
            
            try:
                shipping_date = self._parse_date(row.get('shipping_date', row.get('발송일')))
            except:
                shipping_date = None
            
            try:
                refund_date = self._parse_date(row.get('refund_date', row.get('환불일')))
            except:
                refund_date = None
            
            settlement_data = SmileSettlementData(
                order_number=order_number,
                product_number=product_number,
                cart_number=cart_number,
                product_name=product_name,
                buyer_name=buyer_name,
                payment_confirmation_date=payment_confirmation_date,
                delivery_completion_date=delivery_completion_date,
                early_settlement_date=early_settlement_date,
                settlement_type=settlement_type,
                sales_amount=sales_amount,
                service_fee=service_fee,
                settlement_amount=settlement_amount,
                transfer_amount=transfer_amount,
                payment_date=payment_date,
                shipping_date=shipping_date,
                refund_date=refund_date,
                site=site_value
            )
            
            logger.info(f"정산 데이터 객체 생성 완료 - row {index}: site='{settlement_data.site}'")
            self.processed_count += 1
            return settlement_data
        except Exception as e:
            logger.error(f"정산 데이터 빌드 중 예외 발생 - row {index}: {str(e)}")
            logger.error(f"  예외 타입: {type(e)}")
            logger.error(f"  행 데이터: {dict(row)}")
            self._add_error(index, row, e, "정산")
            return None
    
    def _build_sku_data(self, row: pd.Series, index: int) -> Optional[SmileSkuData]:
        """SKU 데이터 객체 빌드"""
        try:
            sku_data = SmileSkuData(
                sku_number=str(row.get('sku_number', row.get('SKU번호', ''))),
                model_name=str(row.get('model_name', row.get('모델명', ''))),
                sku_name=str(row.get('sku_name', row.get('SKU명', ''))) if pd.notna(row.get('sku_name', row.get('SKU명'))) else None,
                comment=str(row.get('comment', row.get('comment', ''))) if pd.notna(row.get('comment', row.get('comment'))) else None
            )
            self.processed_count += 1
            return sku_data
        except Exception as e:
            self._add_error(index, row, e, "SKU")
            return None
    
    def _parse_date(self, date_value) -> Optional[datetime]:
        """날짜 파싱"""
        if pd.isna(date_value):
            return None
        
        # 특수 값들 처리
        if isinstance(date_value, str):
            date_value = date_value.strip()
            if date_value in ['-', '', 'nan', 'None', 'null']:
                return None
            try:
                return pd.to_datetime(date_value).date()
            except:
                return None
        
        try:
            return date_value.date() if hasattr(date_value, 'date') else date_value
        except:
            return None
    
    def _parse_numeric(self, value) -> Optional[float]:
        """숫자 파싱"""
        if pd.isna(value):
            return None
        try:
            return float(value)
        except:
            return None
    
    def _add_error(self, index: int, row: pd.Series, error: Exception, data_type: str):
        """오류 정보 추가"""
        error_info = SmileDataProcessingErrorDto(
            row_number=index + 1,
            column_name="unknown",
            error_type="data_processing",
            error_message=str(error),
            raw_value=str(row.to_dict())
        )
        self.errors.append(error_info)
        self.skipped_count += 1


class SmileMacroDataBuilder:
    """스마일배송 매크로 데이터 빌더"""
    
    @staticmethod
    def get_column_mapping() -> Dict[str, str]:
        """
        스마일배송 매크로 엑셀 컬럼 매핑 정보 반환
        
        Returns:
            Dict[str, str]: 컬럼 매핑 딕셔너리 (엑셀 컬럼 -> DB 필드)
        """
        return {
            'A': 'fld_dsp',           # 아이디*
            'B': 'expected_payout',   # 정산예정금
            'C': 'service_fee',       # 서비스 이용료
            'D': 'mall_order_id',     # 장바구니번호(결제번호)
            'E': 'pay_cost',          # 금액[배송비미포함]
            'F': 'delv_cost',         # 배송비 금액
            'G': None,                # 구매결정일자 - source_field 없음
            'H': 'mall_product_id',   # 상품번호*
            'I': 'order_id',          # 주문번호*
            'J': 'sku_value',            # 주문옵션
            'K': 'product_name',      # 상품명
            'L': 'item_name',         # 제품명
            'M': 'sale_cnt',          # 수량
            'N': None,                # 추가구성 - source_field 없음
            'O': None,                # 사은품 - source_field 없음
            'P': 'sale_cost',         # 판매금액
            'Q': 'mall_user_id',      # 구매자ID
            'R': 'user_name',         # 구매자명
            'S': 'receive_name',      # 수령인명
            'T': 'delivery_method_str', # 배송비
            'U': 'receive_cel',       # 수령인 휴대폰
            'V': 'receive_tel',       # 수령인 전화번호
            'W': 'receive_addr',      # 주소
            'X': 'receive_zipcode',   # 우편번호
            'Y': 'delv_msg',          # 배송시 요구사항
            'Z': None,                # (옥션)복수구매할인 - source_field 없음
            'AA': None,               # (옥션)우수회원할인 - source_field 없음
            'AB': 'sku1_no',          # SKU1번호
            'AC': 'sku1_cnt',         # SKU1수량
            'AD': 'sku2_no',          # SKU2번호
            'AE': 'sku2_cnt',         # SKU2수량
            'AF': 'sku_no',           # SKU번호 및 수량
            'AG': 'pay_dt',           # 결제완료일
            'AH': 'user_tel',         # 구매자 전화번호
            'AI': 'user_cel',         # 구매자 휴대폰
            'AJ': 'buy_coupon',       # 구매쿠폰적용금액
            'AK': None,               # 발송예정일 - source_field 없음
            'AL': None,               # 발송일자 - source_field 없음
            'AM': None,               # 배송구분 - source_field 없음
            'AN': 'invoice_no',       # 배송번호
            'AO': 'delv_status',      # 배송상태
            'AP': None,               # 배송완료일자 - source_field 없음
            'AQ': None,               # 배송지연사유 - source_field 없음
            'AR': None,               # 배송점포 - source_field 없음
            'AS': None,               # 상품미수령상세사유 - source_field 없음
            'AT': None,               # 상품미수령신고사유 - source_field 없음
            'AU': None,               # 상품미수령신고일자 - source_field 없음
            'AV': None,               # 상품미수령이의제기일자 - source_field 없음
            'AW': None,               # 상품미수령철회요청일자 - source_field 없음
            'AX': None,               # 송장번호(방문수령인증키) - source_field 없음
            'AY': None,               # 일시불할인 - source_field 없음
            'AZ': None,               # 재배송일 - source_field 없음
            'BA': None,               # 재배송지 우편번호 - source_field 없음
            'BB': None,               # 재배송지 운송장번호 - source_field 없음
            'BC': None,               # 재배송지 주소 - source_field 없음
            'BD': None,               # 재배송택배사명 - source_field 없음
            'BE': None,               # 정산완료일 - source_field 없음
            'BF': 'order_dt',         # 주문일자(결제확인전)
            'BG': 'order_method',     # 주문종류
            'BH': None,               # 주문확인일자 - source_field 없음
            'BI': 'delv_method_id',   # 택배사명(발송방법)
            'BJ': None,               # 판매단가 - source_field 없음 (sale_cost와 중복)
            'BK': 'sale_method',      # 판매방식
            'BL': 'order_etc_7',      # 판매자 관리코드
            'BM': None,               # 판매자 상세관리코드 - source_field 없음
            'BN': None,               # 판매자북캐시적립 - source_field 없음
            'BO': 'sale_coupon',      # 판매자쿠폰할인
            'BP': None,               # 판매자포인트적립 - source_field 없음
        }
    
    @staticmethod
    def get_integer_fields() -> set:
        """숫자형 필드 목록 반환"""
        return {'expected_payout', 'service_fee', 'pay_cost', 'delv_cost', 'sale_cost', 'buy_coupon', 'sale_coupon', 'sale_cnt'}
    
    @staticmethod
    def get_date_fields() -> set:
        """날짜형 필드 목록 반환"""
        return {'pay_dt', 'order_dt'}
    
    @staticmethod
    def get_down_form_order_field_types() -> Dict[str, str]:
        """
        down_form_order 필드별 타입 매핑 반환
        
        Returns:
            Dict[str, str]: 필드명 -> 타입 매핑
        """
        return {
            'fld_dsp': 'str',
            'receive_name': 'str',
            'pay_cost': 'integer',
            'order_id': 'str',
            'item_name': 'str',
            'sale_cnt': 'str',  # String(25) 타입
            'receive_cel': 'str',
            'receive_tel': 'str',
            'receive_addr': 'str',
            'receive_zipcode': 'str',
            'delivery_method_str': 'str',
            'mall_product_id': 'str',
            'delv_msg': 'str',
            'expected_payout': 'integer',
            'service_fee': 'integer',
            'mall_order_id': 'str',
            'order_etc_7': 'str',
            'sku_no': 'str',
            'product_name': 'str',
            'delv_cost': 'integer',
            'process_dt': 'datetime',
            'product_id': 'str',
            'invoice_no': 'str'
        }


class SmileDataProcessor:
    """스마일배송 데이터 프로세서"""
    
    def __init__(self, site: str = None):
        self.builder = SmileDataBuilder(site=site)
    
    def process_erp_data(self, df: pd.DataFrame) -> List[SmileErpData]:
        """ERP 데이터 처리"""
        return self.builder.build_erp_data_list(df)
    
    def process_settlement_data(self, df: pd.DataFrame) -> List[SmileSettlementData]:
        """정산 데이터 처리"""
        return self.builder.build_settlement_data_list(df)
    
    def process_sku_data(self, df: pd.DataFrame) -> List[SmileSkuData]:
        """SKU 데이터 처리"""
        return self.builder.build_sku_data_list(df)
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """처리 통계 반환"""
        return {
            "processed_count": self.builder.processed_count,
            "skipped_count": self.builder.skipped_count,
            "errors": self.builder.errors
        }
    
    def reset_stats(self):
        """통계 초기화"""
        self.builder.processed_count = 0
        self.builder.skipped_count = 0
        self.builder.errors = [] 