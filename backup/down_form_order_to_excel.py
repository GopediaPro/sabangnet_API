from utils.excels.convert_xlsx import ConvertXlsx
from sqlalchemy.ext.asyncio import AsyncSession
from models.down_form_orders.down_form_order import BaseDownFormOrder
from schemas.down_form_orders.down_form_order_dto import DownFormOrderDto
from repository.down_form_order_repository import DownFormOrderRepository
from repository.template_config_repository import TemplateConfigRepository


class DownFormOrderToExcel:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.down_form_order_repository = DownFormOrderRepository(self.session)
        self.template_config_repository = TemplateConfigRepository(self.session)

    async def down_form_order_to_excel(self, template_code: str, file_path: str, file_name: str):
        """
        down_form_order_to_excel
        args:
            template_code: template code(gmarket_erp, etc_site_erp ...)
            file_path: file path
            file_name: file name
        returns:
            file_path: file path
        """
        template_config = await self._get_template_config(template_code)
        down_form_orders = await self._get_down_form_orders(template_code)
        mapping_field = await self._create_mapping_field(template_config)

        convert_xlsx = ConvertXlsx()
        file_path = convert_xlsx.export_translated_to_excel(down_form_orders, mapping_field, file_name, file_path="./files/excel")
        return file_path
    
    async def _get_template_config(self, template_code: str) -> list[dict]:
        """
        get template config
        args:
            template_code: template code(gmarket_erp, etc_site_erp ...)
        returns:
            template_config: template_column_mappings data
        """
        
        template_config = await self.template_config_repository.get_template_config_by_template_code(template_code=template_code)
        template_config = template_config["column_mappings"]

        return template_config

    async def _get_down_form_orders(self, template_code: str) -> list[DownFormOrderDto]:
        """
        get down_form_orders
        returns:
            down_form_orders: down_form_orders SQLAlchemy ORM 인스턴스
        """

        down_form_orders: list[DownFormOrderDto] = []

        down_form_order_models: list[BaseDownFormOrder] = await self.down_form_order_repository.get_down_form_orders(template_code=template_code)
        for down_form_order_model in down_form_order_models:
            down_form_orders.append(DownFormOrderDto.model_validate(down_form_order_model))

        return down_form_orders
    
    async def _create_mapping_field(self, template_config: list[dict]) -> dict:
        """
        create mapping field
        args:
            template_config: down_form_order_table[column_mappings]
        returns:
            mapping_field: mapping field {"순번": "seq","사이트": "fld_dsp"...}
        """
        mapping_field = {}
        for col in template_config:
            mapping_field[col["target_column"]] = col["source_field"]
        return mapping_field