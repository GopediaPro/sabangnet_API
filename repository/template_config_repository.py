import json
from typing import Optional
from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession
from models.macro_batch_processing.macro_info import MacroInfo
from utils.unicode_utils import find_matching_item


class TemplateConfigRepository:
    DEFAULT_TEMPLATE_META_QUERY = """
        SELECT id, template_code, template_name, is_aggregated, group_by_fields
        FROM export_templates
        WHERE template_code = :template_code
    """
    COLUMN_MAPPINGS_QUERY = """
        SELECT column_order, target_column, source_field, field_type, aggregation_type, transform_config
        FROM template_column_mappings
        WHERE template_id = :template_id AND is_active = TRUE
        ORDER BY column_order
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def _get_template_meta(self, template_code: str) -> Optional[dict]:
        result = await self.session.execute(
            text(self.DEFAULT_TEMPLATE_META_QUERY),
            {"template_code": template_code}
        )
        row = result.first()
        if not row:
            return None
        return {
            "id": row[0],
            "template_code": row[1],
            "template_name": row[2],
            "is_aggregated": row[3],
            "group_by_fields": row[4] or []
        }

    async def _get_column_mappings(self, template_id: int) -> list[dict]:
        result = await self.session.execute(
            text(self.COLUMN_MAPPINGS_QUERY),
            {"template_id": template_id}
        )
        return [
            {
                "column_order": row[0],
                "target_column": row[1],
                "source_field": row[2],
                "field_type": row[3],
                "aggregation_type": row[4],
                "transform_config": json.loads(row[5]) if isinstance(row[5], str) else row[5] or {}
            }
            for row in result.fetchall()
        ]

    def _merge_columns(self, default_columns: list[dict], input_columns: list[dict]) -> list[dict]:
        columns_by_target = {col["target_column"]
            : col for col in default_columns}
        for col in input_columns:
            columns_by_target[col["target_column"]] = col
        return list(sorted(columns_by_target.values(), key=lambda x: x["column_order"]))

    def _merge_meta(self, default_meta: dict, input_meta: dict) -> dict:
        merged = {**default_meta, **input_meta}
        return merged

    async def get_template_config_by_template_code(self, template_code: str) -> Optional[dict]:
        # Get input template meta and columns
        input_meta = await self._get_template_meta(template_code)
        if not input_meta:
            return None
        input_id = input_meta["id"]
        input_columns = await self._get_column_mappings(input_id)
        return {
            **{k: v for k, v in input_meta.items() if k != "id"},
            "column_mappings": input_columns
        }

    async def get_macro_name_by_template_code(self, template_code: str) -> Optional[str]:
        query = select(MacroInfo.macro_name).where(
            MacroInfo.form_name == template_code)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_macro_name_by_template_code_with_sub_site(self, template_code: str, sub_site: str) -> Optional[str]:
        """
        get macro name by template code and sub_site
        args:
            template_code: template code
            sub_site: sub site (알리, 지그재그, 기타사이트)
        returns:
            macro_name: macro name
        """
        # 모든 매크로 정보를 조회한 후 Python에서 비교
        all_macros_query = select(MacroInfo)
        try:
            all_result = await self.session.execute(all_macros_query)
            all_macros = all_result.scalars().all()

            # 유틸리티 함수를 사용하여 매칭되는 매크로 찾기
            matching_macro = find_matching_item(
                all_macros,
                form_name=template_code,
                sub_site=sub_site
            )

            return matching_macro.macro_name if matching_macro else None

        except Exception as e:
            await self.session.rollback()
            raise e

    async def get_sub_site_true_template_code(self, template_code: str):
        query = select(MacroInfo.sub_site).where(MacroInfo.form_name == template_code)
        result = await self.session.execute(query)
        return result.scalars().first()
