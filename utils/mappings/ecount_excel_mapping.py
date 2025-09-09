"""
Ecount Excel 매핑 유틸리티
Excel 컬럼을 EcountSaleDto 필드로 매핑하는 기능
"""

import pandas as pd
from typing import Dict, Any, Optional
from utils.logs.sabangnet_logger import get_logger

logger = get_logger(__name__)


class EcountExcelMapper:
    """이카운트 Excel 매핑 클래스"""
    
    # Excel 컬럼 매핑 정의
    EXCEL_COLUMN_MAPPING = {
        "일자": "io_date",
        "순번": "upload_ser_no", 
        "거래처코드": "cust",
        "거래처명": "cust_des",
        "담당자": "emp_cd",
        "출하창고": "wh_cd",
        "거래유형": "io_type",
        "통화": "exchange_type",
        "환율": "exchange_rate",
        "E-MAIL": "u_memo1",
        "FAX": "u_memo2",
        "연락처": "u_memo3",
        "주소": "u_txt1",
        "매장판매 결제구분(입금/현금/카드)": "u_memo4",
        "매장판매 거래구분(매장판매/매장구매)": "u_memo5",
        "품목코드": "prod_cd",
        "품목명": "prod_des",
        "수량": "qty",
        "단가": "price",
        "외화금액": "supply_amt_f",
        "공급가액": "supply_amt",
        "부가세": "vat_amt",
        "고객정보(이름/주문번호/연락처/주소/관리코드/장바구니번호)": "remarks",
        "배송메시지": "p_remarks2",
        "송장번호": "p_remarks1",
        "상품번호": "p_remarks3",
        "주문번호": "size_des",
        "정산예정금액": "p_amt1",
        "서비스이용료": "p_amt2",
        "운임비타입": "item_cd"
    }
    
    @classmethod
    def map_excel_row_to_sale_data(cls, row: pd.Series, auth_info=None) -> Dict[str, Any]:
        """
        Excel 행을 판매 데이터로 매핑합니다.
        
        Args:
            row: Excel 행 데이터
            auth_info: 인증 정보 (com_code, user_id 포함)
            
        Returns:
            Dict[str, Any]: 매핑된 판매 데이터
        """
        sale_data = {}
        
        # 인증 정보 설정
        if auth_info:
            sale_data['com_code'] = auth_info.com_code
            sale_data['user_id'] = auth_info.user_id
        
        # Excel 컬럼을 DTO 필드로 매핑
        for excel_col, dto_field in cls.EXCEL_COLUMN_MAPPING.items():
            if excel_col in row.index:
                value = row[excel_col]
                
                # NaN 값 처리
                if pd.isna(value):
                    sale_data[dto_field] = None
                else:
                    # 데이터 타입 변환
                    sale_data[dto_field] = cls._convert_value(value, dto_field)
        
        return sale_data
    
    @classmethod
    def _convert_value(cls, value: Any, dto_field: str) -> Any:
        """
        값을 적절한 데이터 타입으로 변환합니다.
        
        Args:
            value: 변환할 값
            dto_field: DTO 필드명
            
        Returns:
            Any: 변환된 값
        """
        # 정수형 필드
        if dto_field in ['upload_ser_no', 'wh_cd', 'qty', 'price', 
                        'supply_amt_f', 'supply_amt', 'vat_amt', 
                        'exchange_rate', 'p_amt1', 'p_amt2']:
            try:
                return int(float(value)) if value is not None else None
            except (ValueError, TypeError):
                return None
        else:
            # 문자열 필드
            return str(value) if value is not None else None
    
    @classmethod
    def validate_mapping(cls, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Excel 파일의 매핑 유효성을 검증합니다.
        
        Args:
            df: Excel DataFrame
            
        Returns:
            Dict[str, Any]: 검증 결과
        """
        # 컬럼명 정리 (앞뒤 공백 제거)
        df.columns = df.columns.str.strip()
        
        # 매핑 가능한 컬럼 확인
        available_columns = []
        missing_columns = []
        
        for excel_col in cls.EXCEL_COLUMN_MAPPING.keys():
            if excel_col in df.columns:
                available_columns.append(excel_col)
            else:
                missing_columns.append(excel_col)
        
        return {
            "available_columns": available_columns,
            "missing_columns": missing_columns,
            "total_columns": len(df.columns),
            "mapped_columns": len(available_columns),
            "mapping_rate": len(available_columns) / len(cls.EXCEL_COLUMN_MAPPING) * 100
        }
