from utils.sabangnet_logger import get_logger
from sqlalchemy.ext.asyncio import AsyncSession
from repository.down_form_order_repository import DownFormOrderRepository
from models.order.down_form_order import BaseDownFormOrder
from typing import List, Dict, Any
from datetime import datetime
from schemas.order.down_form_order_mapper import map_raw_to_down_form, map_aggregated_to_down_form
from repository.template_config_repository import TemplateConfigRepository

logger = get_logger(__name__)

class DownFormOrderTemplateService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = DownFormOrderRepository(session)
        self.template_config_repo = TemplateConfigRepository(session)

    async def process_and_save(self, template_code: str, raw_data: List[Dict[str, Any]]) -> int:
        logger.info(f"[START] process_and_save | template_code={template_code} | raw_data_count={len(raw_data)}")
        # 1. 템플릿 config 조회
        config = await self.template_config_repo.get_template_config(template_code)
        if not config:
            logger.error(f"Template not found: {template_code}")
            raise ValueError("Template not found")
        logger.info(f"Loaded template config: {config}")

        # 2. 데이터 변환/집계
        processed_data = self._transform_data(raw_data, config)
        logger.info(f"Data processed. processed_data_count={len(processed_data)}")

        # 3. 저장
        objects = [BaseDownFormOrder(**row) for row in processed_data]
        try:
            saved_count = await self.repo.bulk_insert(objects)
            logger.info(f"[END] process_and_save | saved_count={saved_count}")
            return saved_count
        except Exception as e:
            await self.session.rollback()
            logger.error(f"DB Error: {e}")
            raise

    def _transform_data(self, raw_data: List[Dict[str, Any]], config: dict) -> List[Dict[str, Any]]:
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