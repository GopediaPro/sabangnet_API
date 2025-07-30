import os
import re
import hashlib
import pandas as pd
from typing import Any
from decimal import Decimal
from datetime import datetime
from utils.logs.sabangnet_logger import get_logger


logger = get_logger(__name__)


# 개인정보 마스킹 규칙 (ReceiveOrderCreateService._MASKING_RULES와 동일)
MASKING_RULES = {
    'receive_name': 'name',
    'receive_tel': 'phone',
    'receive_cel': 'phone',
    'receive_addr': 'address',
    'receive_zipcode': 'zipcode',
    'order_id': 'id',
    'mall_order_id': 'id',
    'mall_user_id': 'user_id',
}

# 데이터베이스 스키마에 따른 필드 타입 매핑
FIELD_TYPE_MAPPING = {
    # 문자열 필드 (Text, String)
    'idx': 'str',
    'order_id': 'str',
    'mall_order_id': 'str',
    'product_id': 'str',
    'product_name': 'str',
    'mall_product_id': 'str',
    'item_name': 'str',
    'sku_value': 'str',
    'sku_alias': 'str',
    'sku_no': 'str',
    'barcode': 'str',
    'model_name': 'str',
    'erp_model_name': 'str',
    'location_nm': 'str',
    'etc_cost': 'str',
    'price_formula': 'str',
    'receive_name': 'str',
    'receive_cel': 'str',
    'receive_tel': 'str',
    'receive_addr': 'str',
    'receive_zipcode': 'str',
    'delivery_payment_type': 'str',
    'delv_msg': 'str',
    'delivery_id': 'str',
    'delivery_class': 'str',
    'invoice_no': 'str',
    'free_gift': 'str',
    'etc_msg': 'str',
    'order_etc_7': 'str',
    'fld_dsp': 'str',
    'order_etc_6': 'str',
    'reg_date': 'str',
    'ord_confirm_date': 'str',
    'rtn_dt': 'str',
    'chng_dt': 'str',
    'delivery_confirm_date': 'str',
    'cancel_dt': 'str',
    'hope_delv_date': 'str',
    'inv_send_dm': 'str',
    'work_status': 'str',
    'form_name': 'str',

    # 정수 필드 (Integer)
    'seq': 'int',
    'sale_cnt': 'int',

    # Decimal 필드 (Numeric)
    'pay_cost': 'decimal',
    'delv_cost': 'decimal',
    'total_cost': 'decimal',
    'total_delv_cost': 'decimal',
    'expected_payout': 'decimal',
    'service_fee': 'decimal',
    'sum_p_ea': 'decimal',
    'sum_expected_payout': 'decimal',
    'sum_pay_cost': 'decimal',
    'sum_delv_cost': 'decimal',
    'sum_total_cost': 'decimal',

    # 날짜 필드 (DateTime, TIMESTAMP)
    'process_dt': 'datetime',
    'order_date': 'datetime',

    # JSONB 필드
    'error_logs': 'jsonb',
}

def convert_field_to_db_type(field_name: str, value: Any) -> Any:
    """
    데이터베이스 스키마에 맞게 필드 값을 변환하는 공통 메서드
    
    Args:
        field_name: 필드명
        value: 변환할 값
        
    Returns:
        변환된 값
    """
    if value is None:
        return None
    
    field_type = FIELD_TYPE_MAPPING.get(field_name)
    if not field_type:
        # 매핑되지 않은 필드는 원본 값 반환
        return value
    
    try:
        if field_type == 'str':
            str_value = str(value)
            
            # String 필드들의 길이 제한 적용
            if field_name == 'delivery_payment_type' and len(str_value) > 10:
                logger.warning(f"delivery_payment_type value too long: {str_value}, truncating to 10 characters")
                return str_value[:10]
            elif field_name == 'form_name' and len(str_value) > 30:
                logger.warning(f"form_name value too long: {str_value}, truncating to 30 characters")
                return str_value[:30]
            elif field_name == 'order_id' and len(str_value) > 100:
                logger.warning(f"order_id value too long: {str_value}, truncating to 100 characters")
                return str_value[:100]
            elif field_name == 'mall_product_id' and len(str_value) > 50:
                logger.warning(f"mall_product_id value too long: {str_value}, truncating to 50 characters")
                return str_value[:50]
            elif field_name == 'item_name' and len(str_value) > 100:
                logger.warning(f"item_name value too long: {str_value}, truncating to 100 characters")
                return str_value[:100]
            elif field_name == 'receive_name' and len(str_value) > 100:
                logger.warning(f"receive_name value too long: {str_value}, truncating to 100 characters")
                return str_value[:100]
            elif field_name == 'receive_cel' and len(str_value) > 20:
                logger.warning(f"receive_cel value too long: {str_value}, truncating to 20 characters")
                return str_value[:20]
            elif field_name == 'receive_tel' and len(str_value) > 20:
                logger.warning(f"receive_tel value too long: {str_value}, truncating to 20 characters")
                return str_value[:20]
            elif field_name == 'receive_zipcode' and len(str_value) > 15:
                logger.warning(f"receive_zipcode value too long: {str_value}, truncating to 15 characters")
                return str_value[:15]
            elif field_name == 'price_formula' and len(str_value) > 50:
                logger.warning(f"price_formula value too long: {str_value}, truncating to 50 characters")
                return str_value[:50]
            elif field_name == 'work_status' and len(str_value) > 14:
                logger.warning(f"work_status value too long: {str_value}, truncating to 14 characters")
                return str_value[:14]
            elif field_name == 'idx' and len(str_value) > 50:
                logger.warning(f"idx value too long: {str_value}, truncating to 50 characters")
                return str_value[:50]
            elif field_name == 'reg_date' and len(str_value) > 14:
                logger.warning(f"reg_date value too long: {str_value}, truncating to 14 characters")
                return str_value[:14]
            elif field_name == 'ord_confirm_date' and len(str_value) > 14:
                logger.warning(f"ord_confirm_date value too long: {str_value}, truncating to 14 characters")
                return str_value[:14]
            elif field_name == 'rtn_dt' and len(str_value) > 14:
                logger.warning(f"rtn_dt value too long: {str_value}, truncating to 14 characters")
                return str_value[:14]
            elif field_name == 'chng_dt' and len(str_value) > 14:
                logger.warning(f"chng_dt value too long: {str_value}, truncating to 14 characters")
                return str_value[:14]
            elif field_name == 'delivery_confirm_date' and len(str_value) > 14:
                logger.warning(f"delivery_confirm_date value too long: {str_value}, truncating to 14 characters")
                return str_value[:14]
            elif field_name == 'cancel_dt' and len(str_value) > 14:
                logger.warning(f"cancel_dt value too long: {str_value}, truncating to 14 characters")
                return str_value[:14]
            elif field_name == 'hope_delv_date' and len(str_value) > 14:
                logger.warning(f"hope_delv_date value too long: {str_value}, truncating to 14 characters")
                return str_value[:14]
            elif field_name == 'inv_send_dm' and len(str_value) > 14:
                logger.warning(f"inv_send_dm value too long: {str_value}, truncating to 14 characters")
                return str_value[:14]
            
            return str_value
        elif field_type == 'int':
            if isinstance(value, str) and value.strip() == '':
                return None
            return int(float(value)) if value else None
        elif field_type == 'decimal':
            if isinstance(value, str) and value.strip() == '':
                return None
            return Decimal(str(value)) if value else None
        elif field_type == 'datetime':
            if isinstance(value, str) and value.strip() == '':
                return None
            if isinstance(value, datetime):
                return value
            # 문자열을 datetime으로 변환하는 로직 추가 가능
            return value
        elif field_type == 'jsonb':
            # JSONB 타입은 원본 값 반환 (이미 적절한 형태일 것으로 가정)
            return value
        else:
            return value
    except (ValueError, TypeError) as e:
        logger.warning(f"Field {field_name} conversion failed: {value} -> {field_type}, error: {e}")
        return value

def convert_row_to_db_types(row: dict[str, Any]) -> dict[str, Any]:
    """
    전체 row의 모든 필드를 데이터베이스 스키마에 맞게 변환

    Args:
        row: 변환할 데이터 row

    Returns:
        변환된 row
    """
    converted_row = {}
    for field_name, value in row.items():
        converted_row[field_name] = convert_field_to_db_type(field_name, value)
    return converted_row

def _mask_personal_info(value: str, mask_type: str) -> str:
    if not value or str(value).strip() == '':
        return value
    value = str(value)
    if mask_type == 'name':
        if len(value) <= 1:
            return '*'
        return value[0] + '*' * (len(value) - 1)
    elif mask_type == 'phone':
        phone_digits = re.sub(r'[^0-9]', '', value)
        if len(phone_digits) >= 8:
            if len(phone_digits) == 11:
                return phone_digits[:3] + '****' + phone_digits[7:]
            elif len(phone_digits) == 10:
                return phone_digits[:3] + '****' + phone_digits[6:]
        return '****'
    elif mask_type == 'address':
        parts = value.split()
        if len(parts) > 2:
            return ' '.join(parts[:2]) + ' ****'
        return '****'
    elif mask_type == 'zipcode':
        if len(value) >= 3:
            return value[:3] + '*' * (len(value) - 3)
        return '*' * len(value)
    elif mask_type == 'id':
        return hashlib.md5(value.encode()).hexdigest()[:8]
    elif mask_type == 'user_id':
        if len(value) > 2:
            return value[:2] + '*' * (len(value) - 2)
        return '*' * len(value)
    return value

def map_raw_to_down_form(raw_row: dict[str, Any], config: dict) -> dict[str, Any]:
    """
    단일 row를 down_form_orders 스키마에 맞게 변환
    config['column_mappings']를 참고하여 동적으로 매핑
    """
    mapped = {}
    for col in config['column_mappings']:
        field = col['source_field']
        # taget은 excel input, export 용 컬럼명
        # target = col['target_column']
        field_type = col.get('field_type')
        transform_config = col.get('transform_config', {})
        # variable: 원본 그대로
        if field_type == 'variable':
            mapped[field] = raw_row.get(field)
        # formula: 수식/가공
        elif field_type == 'formula':
            mapped[field] = eval_formula(transform_config, raw_row)
        # empty: 빈 값
        elif field_type == 'empty':
            mapped[field] = None
        # constant: 상수
        # elif field_type == 'constant':
        #     mapped[target] = transform_config.get('value')
        else:
            mapped[field] = raw_row.get(field)

    # 데이터베이스 스키마에 맞게 타입 변환
    mapped = convert_row_to_db_types(mapped)

    return mapped

def map_aggregated_to_down_form(group_rows: list[dict[str, Any]], config: dict) -> dict[str, Any]:
    """
    집계 row를 down_form_orders 스키마에 맞게 변환
    aggregation_type에 따라 sum/first 등 처리
    """
    mapped = {}
    for col in config['column_mappings']:
        field = col['source_field']
        # target = col['target_column']
        agg_type = col.get('aggregation_type')
        if agg_type == 'sum':
            mapped[field] = sum(row.get(field, 0) or 0 for row in group_rows)
        elif agg_type == 'first':
            mapped[field] = group_rows[0].get(field)
        elif agg_type == 'concat':
            mapped[field] = ','.join(str(row.get(field, '')) for row in group_rows)
        else:  # none
            mapped[field] = group_rows[0].get(field)

    # 데이터베이스 스키마에 맞게 타입 변환
    mapped = convert_row_to_db_types(mapped)

    return mapped

def eval_formula(transform_config: dict, row: dict) -> Any:
    # 실제 수식 파싱/계산 로직 필요 (예: "sku_alias + ' ' + sale_cnt + '개'")
    # 예시: 단순 파이썬 eval 사용 (보안상 실제 서비스에서는 안전하게 구현 필요)
    try:
        source = transform_config.get('source')
        if source:
            return eval(source, {}, row)
    except Exception:
        return None

def map_excel_to_down_form(df: pd.DataFrame, config: dict) -> list[dict[str, Any]]:
    """
    excel 데이터를 down_form_orders 스키마에 맞게 변환
    """
    column_mappings = config.get('column_mappings', [])
    # target_column(엑셀 컬럼명) -> source_field(DB 필드명) 매핑 dict
    col_map = {col['target_column']: col['source_field'] for col in column_mappings}
    logger.info(f"col_map: {col_map}")
    raw_data = []
    # 엑셀 데이터 → DB 저장용 dict 변환
    is_test_env = os.getenv("DEPLOY_ENV", "production") != "production"
    for _, row in df.iterrows():
        mapped_row = {col_map.get(col, col): row[col] for col in df.columns if col in col_map}

        # 데이터베이스 스키마에 맞게 타입 변환
        mapped_row = convert_row_to_db_types(mapped_row)

        # 개인정보 마스킹 (TEST 환경에서만)
        if is_test_env:
            for field, mask_type in MASKING_RULES.items():
                if field in mapped_row and mapped_row[field]:
                    mapped_row[field] = _mask_personal_info(mapped_row[field], mask_type)
        raw_data.append(mapped_row)
    return raw_data