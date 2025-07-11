from typing import Dict, Any, List
import pandas as pd

def map_raw_to_down_form(raw_row: Dict[str, Any], config: dict) -> Dict[str, Any]:
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

def map_aggregated_to_down_form(group_rows: List[Dict[str, Any]], config: dict) -> Dict[str, Any]:
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

def map_excel_to_down_form(df: pd.DataFrame, config: dict) -> Dict[str, Any]:
    """
    excel 데이터를 down_form_orders 스키마에 맞게 변환
    """
    column_mappings = config.get('column_mappings', [])
    # target_column(엑셀 컬럼명) -> source_field(DB 필드명) 매핑 dict
    col_map = {col['target_column']: col['source_field'] for col in column_mappings}
    raw_data = []
    # 엑셀 데이터 → DB 저장용 dict 변환
    for _, row in df.iterrows():
        mapped_row = {col_map.get(col, col): row[col] for col in df.columns if col in col_map}
        raw_data.append(mapped_row)
    return raw_data