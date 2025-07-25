from repository.export_templates_repository import ExportTemplateRepository
from models.config.export_templates import ExportTemplates
from sqlalchemy.ext.asyncio import AsyncSession


class ExportTemplatesReadService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.export_template_repository = ExportTemplateRepository(session)

    async def get_export_templates(self) -> list[ExportTemplates]:
        return await self.export_template_repository.get_export_templates()

    async def get_export_templates_code_and_name(self) -> list[dict[str, str]]:
        export_templates = await self.export_template_repository.get_export_templates()
        export_templates_code_and_name = []
        for export_template in export_templates:
            export_templates_code_and_name.append(
                {
                    "template_code": export_template.template_code,
                    "template_name": export_template.template_name
                }
            )
        return export_templates_code_and_name