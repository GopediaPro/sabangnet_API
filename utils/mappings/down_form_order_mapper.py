import os
import re
import hashlib
import pandas as pd
from typing import Any
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
        # idx를 str로 변환
        if 'idx' in mapped_row and mapped_row['idx'] is not None:
            mapped_row['idx'] = str(mapped_row['idx'])
        # 개인정보 마스킹 (TEST 환경에서만)
        if is_test_env:
            for field, mask_type in MASKING_RULES.items():
                if field in mapped_row and mapped_row[field]:
                    mapped_row[field] = _mask_personal_info(mapped_row[field], mask_type)
        raw_data.append(mapped_row)
    return raw_data