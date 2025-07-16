from sqlalchemy.ext.asyncio import AsyncSession
from repository.template_config_repository import TemplateConfigRepository


class TemplateConfigReadService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.template_config_repository = TemplateConfigRepository(session)

    async def get_template_config_by_template_code(self, template_code: str) -> dict:
        """
        get template config
        args:
            template_code: template code(gmarket_erp, etc_site_erp ...)
        returns:
            template_config: 전체 템플릿 설정 (column_mappings 포함)
        """
        
        template_config = await self.template_config_repository.get_template_config_by_template_code(template_code=template_code)
        return template_config