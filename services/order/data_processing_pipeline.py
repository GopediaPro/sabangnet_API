from utils.sabangnet_logger import get_logger
logger = get_logger(__name__)
from sqlalchemy.ext.asyncio import AsyncSession
from models.order.down_form_order import BaseDownFormOrder
from typing import Dict, List, Any
from datetime import datetime
from schemas.order.down_form_order_mapper import map_raw_to_down_form, map_aggregated_to_down_form, map_excel_to_down_form
from repository.template_config_repository import TemplateConfigRepository
import requests
import tempfile
from utils.excel_handler import ExcelHandler
import os
import pandas as pd

class DataProcessingPipeline:
    def __init__(self, session: AsyncSession):
        self.session = session
        # 변환 함수들
        self.transformers = {
            "convert_delivery_method": self._convert_delivery_method,
            "sku_quantity": self._sku_quantity,
            "barcode_quantity": self._barcode_quantity,
            "calculate_service_fee": self._calculate_service_fee,
        }
        self.template_config_repo = TemplateConfigRepository(session)

    def _extract_datetime_fields(self, raw_row: dict) -> dict:
        """
        raw_row에서 날짜/시간 관련 필드만 추출하여 dict로 반환
        """
        datetime_fields = [
            'order_date',
            'reg_date',
            'ord_confirm_date',
            'rtn_dt',
            'chng_dt',
            'delivery_confirm_date',
            'cancel_dt',
            'hope_delv_date',
            'inv_send_dm',
        ]
        return {field: raw_row.get(field) for field in datetime_fields if field in raw_row}

    async def process_raw_data_to_down_form_orders(self, 
                                                  raw_data: List[Dict[str, Any]], 
                                                  template_code: str) -> int:
        logger.info(f"[START] process_raw_data_to_down_form_orders | template_code={template_code} | raw_data_count={len(raw_data)}")
        """
        메인 프로세스: 원본 데이터 -> 템플릿별 변환 -> down_form_orders 저장
        
        Args:
            raw_data: receive_orders 테이블에서 가져온 원본 데이터
            template_code: 적용할 템플릿 코드 (예: 'gmarket_erp')
        
        Returns:
            저장된 레코드 수
        """
        # 1. 템플릿 설정 조회
        config = await self.template_config_repo.get_template_config(template_code)
        if not config:
            logger.error(f"Template not found: {template_code}")
            raise ValueError("Template not found")
        logger.info(f"Loaded template config: {config}")

        # 2. 템플릿에 따라 데이터 변환
        if config['is_aggregated']: 
            logger.info("Aggregated template detected. Processing aggregated data.")
            processed_data = await self._process_aggregated_data(raw_data, config)
        else:
            logger.info("Simple template detected. Processing simple data.")
            processed_data = await self._process_simple_data(raw_data, config)
        logger.info(f"Data processed. processed_data_count={len(processed_data)}. Sample: {processed_data[:3]}")
        
        # 3. down_form_orders에 저장
        saved_count = await self._save_to_down_form_orders(processed_data, template_code)
        logger.info(f"[END] process_raw_data_to_down_form_orders | saved_count={saved_count}")
        return saved_count
    
    async def _process_simple_data(self, 
                                 raw_data: List[Dict[str, Any]], 
                                 config: dict) -> List[Dict[str, Any]]:
        """단순 변환 (1:1 매핑)"""
        processed_data = []
        for seq, raw_row in enumerate(raw_data, start=1):
            processed_row = {
                'process_dt': datetime.now(),
                'form_name': config['template_code'],
                'seq': seq,
            }
            # 날짜/시간 필드 추가
            processed_row.update(self._extract_datetime_fields(raw_row))
            processed_row.update(map_raw_to_down_form(raw_row, config))
            processed_data.append(processed_row)
        return processed_data
    
    async def _process_aggregated_data(self, 
                                     raw_data: List[Dict[str, Any]], 
                                     config: dict) -> List[Dict[str, Any]]:
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
            # 대표 row에서 날짜/시간 필드 추출 (첫 row 기준)
            processed_row.update(self._extract_datetime_fields(group_rows[0]))
            processed_row.update(map_aggregated_to_down_form(group_rows, config))
            processed_data.append(processed_row)
        return processed_data
       
    async def _save_to_down_form_orders(self, processed_data: List[Dict[str, Any]], template_code: str) -> int:
        logger.info(f"[START] _save_to_down_form_orders | processed_data_count={len(processed_data)} | template_code={template_code}")
        if not processed_data:
            logger.warning("No processed data to save.")
            return 0
        try:
            objects = [BaseDownFormOrder(**row) for row in processed_data]
            self.session.add_all(objects)
            await self.session.commit()
            logger.info(f"[END] _save_to_down_form_orders | saved_count={len(objects)}")
            return len(objects)
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Exception during _save_to_down_form_orders: {e}")
            raise

    async def _process_excel_data(self, df, config):
        """
        DataFrame과 config(column_mappings)를 받아 DB 저장용 dict 리스트로 변환
        """
        raw_data = map_excel_to_down_form(df, config)
        processed_data = []
        for seq, raw_row in enumerate(raw_data, start=1):
            processed_row = {
                'process_dt': datetime.now(),
                'form_name': config['template_code'],
                'seq': seq,
            }
            processed_row.update(raw_row)
            processed_data.append(processed_row)
        return processed_data
    
    async def process_excel_to_down_form_orders(self, df, template_code: str) -> int:
        """
        Excel 파일을 읽어 config 매핑에 따라 데이터를 DB에 저장
        Args:
            excel_file: Excel 파일
            template_code: 템플릿 코드
        Returns:
            저장된 레코드 수
        """
        logger.info(f"[START] process_excel_to_down_form_orders | template_code={template_code} | df_count={len(df)}")
        # 1. config 매핑 정보 조회
        config = await self.template_config_repo.get_template_config(template_code)
        logger.info(f"Loaded template config: {config}")
        # 2. 엑셀 데이터 변환
        raw_data = await self._process_excel_data(df, config)
        # 3. DB 저장
        saved_count = await self._save_to_down_form_orders(raw_data, template_code)
        logger.info(f"[END] process_excel_to_down_form_orders | saved_count={saved_count}")
        return saved_count
    
    def _from_db_to_df(self, db_data: list[dict], config: dict) -> pd.DataFrame:
        """
        DB 데이터를 DataFrame으로 변환 (config의 source_field→target_column 매핑 적용)
        """
        column_mappings = config.get('column_mappings', [])
        # source_field → target_column 매핑 dict 생성
        field_to_column = {m['source_field']: m['target_column'] for m in column_mappings}
        # 변환된 row 리스트 생성
        converted_rows = []
        for row in db_data:
            converted_row = {}
            for source_field, target_column in field_to_column.items():
                converted_row[target_column] = row.get(source_field)
            converted_rows.append(converted_row)
        df = pd.DataFrame(converted_rows)
        return df

    # 변환 함수들
    def _convert_delivery_method(self, value: Any, context: Dict[str, Any]) -> str:
        if not value:
            return ""
        mapping = {"credit": "선불", "cod": "착불", "prepaid": "선불"}
        return mapping.get(str(value).lower(), str(value))
    
    def _sku_quantity(self, value: Any, context: Dict[str, Any]) -> str:
        sku_alias = context.get('sku_alias', '') or value or ''
        sale_cnt = context.get('sale_cnt', 0) or 0
        return f"{sku_alias} {sale_cnt}개" if sku_alias else ""
    
    def _barcode_quantity(self, value: Any, context: Dict[str, Any]) -> str:
        barcode = context.get('barcode', '') or value or ''
        sale_cnt = context.get('sale_cnt', 0) or 0
        return f"{barcode} {sale_cnt}개" if barcode else ""
    
    def _calculate_service_fee(self, value: Any, context: Dict[str, Any]) -> int:
        pay_cost = context.get('pay_cost', 0) or 0
        mall_won_cost = context.get('mall_won_cost', 0) or 0
        sale_cnt = context.get('sale_cnt', 0) or 0
        return int(pay_cost - (mall_won_cost * sale_cnt))