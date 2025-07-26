import pandas as pd
from typing import Any
from datetime import datetime
from utils.mappings.down_form_order_mapper import (
    map_raw_to_down_form,
    map_excel_to_down_form,
    map_aggregated_to_down_form,
)


class DataProcessingUtils:
    """작업 처리용 함수 모아놓은 클래스"""

    @staticmethod
    def convert_delivery_method(value: Any) -> str:
        if not value:
            return ""
        mapping = {"credit": "선불", "cod": "착불", "prepaid": "선불"}
        return mapping.get(str(value).lower(), str(value))
    
    @staticmethod
    def sku_quantity(value: Any, context: dict[str, Any]) -> str:
        sku_alias = context.get('sku_alias', '') or value or ''
        sale_cnt = context.get('sale_cnt', 0) or 0
        return f"{sku_alias} {sale_cnt}개" if sku_alias else ""
    
    @staticmethod
    def barcode_quantity(value: Any, context: dict[str, Any]) -> str:
        barcode = context.get('barcode', '') or value or ''
        sale_cnt = context.get('sale_cnt', 0) or 0
        return f"{barcode} {sale_cnt}개" if barcode else ""
    
    @staticmethod
    def calculate_service_fee(value: Any, context: dict[str, Any]) -> int:
        pay_cost = context.get('pay_cost', 0) or 0
        mall_won_cost = context.get('mall_won_cost', 0) or 0
        sale_cnt = context.get('sale_cnt', 0) or 0
        return int(pay_cost - (mall_won_cost * sale_cnt))
    
    @staticmethod
    def transform_data(raw_data: list[dict[str, Any]], config: dict) -> list[dict[str, Any]]:
        processed_data = []
        if config.get('is_aggregated'):
            group_by = config.get('group_by_fields', [])
            grouped = {}
            for row in raw_data:
                key = tuple(row.get(f) for f in group_by)
                grouped.setdefault(key, []).append(row)
            for seq, (key, group_rows) in enumerate(grouped.items(), start=1):
                base = {
                    'process_dt': datetime.now(),
                    'form_name': config['template_code'],
                    'seq': seq,
                }
                base.update(map_aggregated_to_down_form(group_rows, config))
                processed_data.append(base)
        else:
            for seq, row in enumerate(raw_data, start=1):
                base = {
                    'process_dt': datetime.now(),
                    'form_name': config['template_code'],
                    'seq': seq,
                }
                base.update(map_raw_to_down_form(row, config))
                processed_data.append(base)
        return processed_data     
    
    @staticmethod
    async def create_mapping_field(template_config: dict) -> dict:
        """
        create mapping field
        args:
            template_config: 전체 템플릿 설정 (column_mappings 포함)
        returns:
            mapping_field: mapping field {"순번": "seq","사이트": "fld_dsp"...}
        """
        mapping_field = {}
        for col in template_config["column_mappings"]:
            mapping_field[col["target_column"]] = col["source_field"]
        return mapping_field

    @staticmethod
    async def process_simple_data(
            raw_data: list[dict[str, Any]],
            config: dict
        ) -> list[dict[str, Any]]:
        """단순 변환 (1:1 매핑)"""
        processed_data = []
        for seq, raw_row in enumerate(raw_data, start=1):
            processed_row = {
                'process_dt': datetime.now(),
                'form_name': config['template_code'],
                'seq': seq,
            }
            processed_row.update(map_raw_to_down_form(raw_row, config))
            processed_data.append(processed_row)
        return processed_data
    
    @staticmethod
    async def process_aggregated_data(
            raw_data: list[dict[str, Any]],
            config: dict
        ) -> list[dict[str, Any]]:
        """집계 변환 (합포장용)"""
        grouped_data = {}
        group_field_mapping = {
            'order_id': 'order_id',
            'receive_name': 'receive_name', 
            'receive_addr': 'receive_addr'
        }
        for raw_row in raw_data:
            group_key = tuple(
                raw_row.get(group_field_mapping.get(field, field), '') 
                for field in config['group_by_fields']
            )
            if group_key not in grouped_data:
                grouped_data[group_key] = []
            grouped_data[group_key].append(raw_row)
        processed_data = []
        for seq, (group_key, group_rows) in enumerate(grouped_data.items(), start=1):
            processed_row = {
                'process_dt': datetime.now(),
                'form_name': config['template_code'],
                'seq': seq,
            }
            processed_row.update(map_aggregated_to_down_form(group_rows, config))
            processed_data.append(processed_row)
        return processed_data

    @staticmethod
    async def process_excel_data(df: pd.DataFrame, config: dict, work_status: str = None) -> list[dict[str, Any]]:
        """
        args:
            df: data frame
            config: config (column_mappings)
            work_status: 매크로 작업 상태 (macro_run, etc...)
        returns:
            processed_data: db 저장용 dict 리스트
        """
        raw_data: list[dict[str, Any]] = map_excel_to_down_form(df, config)
        processed_data = []
        for seq, raw_row in enumerate(raw_data, start=1):
            processed_row = raw_row.copy()
            processed_row.update({
                'process_dt': datetime.now(),
                'form_name': config['template_code'],
                'seq': seq,
                'work_status': work_status,
            })
            processed_data.append(processed_row)
        return processed_data
