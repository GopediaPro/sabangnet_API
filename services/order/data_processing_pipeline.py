from utils.sabangnet_logger import get_logger
logger = get_logger(__name__)
from sqlalchemy.ext.asyncio import AsyncSession
from models.order.down_form_order import DownFormOrder
from typing import Dict, List, Any
from datetime import datetime
from schemas.order.down_form_order_mapper import map_raw_to_down_form, map_aggregated_to_down_form
from repository.template_config_repository import TemplateConfigRepository
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
            processed_row.update(map_aggregated_to_down_form(group_rows, config))
            processed_data.append(processed_row)
        return processed_data
    
    async def _save_to_down_form_orders(self, processed_data: List[Dict[str, Any]], template_code: str) -> int:
        logger.info(f"[START] _save_to_down_form_orders | processed_data_count={len(processed_data)} | template_code={template_code}")
        if not processed_data:
            logger.warning("No processed data to save.")
            return 0
        try:
            objects = [DownFormOrder(**row) for row in processed_data]
            self.session.add_all(objects)
            await self.session.commit()
            logger.info(f"[END] _save_to_down_form_orders | saved_count={len(objects)}")
            return len(objects)
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Exception during _save_to_down_form_orders: {e}")
            raise
    
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