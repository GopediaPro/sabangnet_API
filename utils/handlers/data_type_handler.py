"""
Data Type Handler
데이터 타입 변환을 위한 유틸리티 핸들러
"""

from typing import Any, Optional
from datetime import datetime
from decimal import Decimal
import re


class DataTypeHandler:
    """데이터 타입 변환 핸들러"""
    
    @staticmethod
    def to_integer(value: Any) -> Optional[int]:
        """
        값을 정수형으로 변환
        
        Args:
            value: 변환할 값
            
        Returns:
            Optional[int]: 변환된 정수값, 실패 시 None
        """
        if value is None:
            return None
        
        try:
            str_value = str(value).strip()
            if not str_value:
                return None
            
            # 쉼표 제거
            str_value = str_value.replace(',', '')
            # 원화 기호 제거
            str_value = str_value.replace('₩', '').replace('원', '')
            
            # 괄호 제거 (음수 표시용)
            is_negative = False
            if str_value.startswith('(') and str_value.endswith(')'):
                str_value = str_value[1:-1]  # 괄호 제거
                is_negative = True
            
            if not str_value:
                return None
            
            # 소수점이 있는 경우 정수로 변환
            result = int(float(str_value))
            return -result if is_negative else result
            
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def to_float(value: Any) -> Optional[float]:
        """
        값을 실수형으로 변환
        
        Args:
            value: 변환할 값
            
        Returns:
            Optional[float]: 변환된 실수값, 실패 시 None
        """
        if value is None:
            return None
        
        try:
            str_value = str(value).strip()
            if not str_value:
                return None
            
            # 문자열 정리 (쉼표, 원화 기호, 공백 제거)
            cleaned_value = DataTypeHandler._clean_numeric_string(str_value)
            if not cleaned_value:
                return None
            
            return float(cleaned_value)
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def to_decimal(value: Any) -> Optional[Decimal]:
        """
        값을 Decimal 타입으로 변환
        
        Args:
            value: 변환할 값
            
        Returns:
            Optional[Decimal]: 변환된 Decimal값, 실패 시 None
        """
        if value is None:
            return None
        
        try:
            str_value = str(value).strip()
            if not str_value:
                return None
            
            # 문자열 정리 (쉼표, 원화 기호, 공백 제거)
            cleaned_value = DataTypeHandler._clean_numeric_string(str_value)
            if not cleaned_value:
                return None
            
            return Decimal(cleaned_value)
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def to_date(value: Any) -> Optional[datetime]:
        """
        값을 날짜형으로 변환
        
        Args:
            value: 변환할 값
            
        Returns:
            Optional[datetime]: 변환된 날짜값, 실패 시 None
        """
        if value is None:
            return None
        
        try:
            str_value = str(value).strip()
            if not str_value:
                return None
            
            # 특수 값들 처리
            if str_value.lower() in ['-', '', 'nan', 'none', 'null']:
                return None
            
            # 이미 datetime 객체인 경우
            if isinstance(value, datetime):
                return value
            
            # pandas Timestamp인 경우
            if hasattr(value, 'date'):
                return value.date()
            
            # 문자열 날짜 파싱
            return DataTypeHandler._parse_date_string(str_value)
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def to_string(value: Any) -> Optional[str]:
        """
        값을 문자열로 변환
        
        Args:
            value: 변환할 값
            
        Returns:
            Optional[str]: 변환된 문자열, 실패 시 빈 문자열
        """
        if value is None:
            return ""
        
        try:
            # float인 경우 정수로 변환 후 문자열로 변환
            if isinstance(value, float):
                # 소수점이 0인 경우에만 정수로 변환
                if value.is_integer():
                    value = int(value)
                else:
                    # 소수점이 있는 경우 그대로 유지
                    pass
            
            str_value = str(value).strip()
            return str_value if str_value else ""
        except (ValueError, TypeError):
            return ""
    
    @staticmethod
    def _clean_numeric_string(value: str) -> str:
        """
        숫자 문자열 정리 (쉼표, 원화 기호, 공백 제거)
        
        Args:
            value: 정리할 문자열
            
        Returns:
            str: 정리된 문자열
        """
        # 쉼표, 원화 기호, 공백 제거
        cleaned = value.replace(',', '').replace('₩', '').replace('원', '').strip()
        
        # 숫자와 소수점만 남기고 제거
        cleaned = re.sub(r'[^\d.-]', '', cleaned)
        
        return cleaned
    
    @staticmethod
    def _parse_date_string(date_str: str) -> Optional[datetime]:
        """
        날짜 문자열 파싱
        
        Args:
            date_str: 파싱할 날짜 문자열
            
        Returns:
            Optional[datetime]: 파싱된 날짜, 실패 시 None
        """
        try:
            # YYYY-MM-DD 형식
            if len(date_str) == 10 and date_str.count('-') == 2:
                return datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # YYYYMMDD 형식
            elif len(date_str) == 8 and date_str.isdigit():
                return datetime.strptime(date_str, '%Y%m%d').date()
            
            # YYYY/MM/DD 형식
            elif len(date_str) == 10 and date_str.count('/') == 2:
                return datetime.strptime(date_str, '%Y/%m/%d').date()
            
            # MM/DD/YYYY 형식
            elif len(date_str) == 10 and date_str.count('/') == 2:
                return datetime.strptime(date_str, '%m/%d/%Y').date()
            
            # pandas to_datetime 사용
            import pandas as pd
            return pd.to_datetime(date_str).date()
            
        except (ValueError, TypeError):
            return None


class SmileDataTypeHandler(DataTypeHandler):
    """스마일배송 전용 데이터 타입 핸들러"""
    
    @staticmethod
    def convert_field_value(value: Any, field_name: str, field_type: str) -> Any:
        """
        필드 타입에 따라 값을 변환
        
        Args:
            value: 변환할 값
            field_name: 필드명
            field_type: 필드 타입 ('integer', 'numeric', 'date', 'datetime', 'string')
            
        Returns:
            Any: 변환된 값
        """
        if field_type == 'integer':
            return SmileDataTypeHandler.to_integer(value)
        elif field_type == 'date':
            return SmileDataTypeHandler.to_date(value)
        elif field_type == 'datetime':
            # datetime 타입은 이미 datetime 객체이거나 None인 경우 그대로 반환
            if isinstance(value, datetime):
                return value
            elif value is None:
                return None
            else:
                # 문자열을 datetime으로 변환 시도
                return SmileDataTypeHandler.to_date(value)
        elif field_type == 'string':
            return SmileDataTypeHandler.to_string(value)
        else:
            # 기본적으로 문자열로 변환
            return SmileDataTypeHandler.to_string(value)
    
    @staticmethod
    def get_field_type(field_name: str, integer_fields: set, date_fields: set) -> str:
        """
        필드명에 따른 타입 반환
        
        Args:
            field_name: 필드명
            numeric_fields: 숫자형 필드 집합
            integer_fields: 정수형 필드 집합
            date_fields: 날짜형 필드 집합
            
        Returns:
            str: 필드 타입
        """
        if field_name in integer_fields:
            return 'integer' 
        elif field_name in date_fields:
            return 'date'
        else:
            return 'string'
