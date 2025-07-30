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

    async def find_template_code_by_site_usage_star(self, site_type: str, usage_type: str, is_star: bool) -> str:
        """
        site_type, usage_type, is_star를 기반으로 template_code를 찾는 메서드
        args:
            site_type: 사이트타입 (G마켓,옥션, 기본양식, 브랜디 등)
            usage_type: 용도타입 (ERP용, 합포장용)
            is_star: 스타배송 여부
        returns:
            template_code: 템플릿 코드
        """
        return await self.export_template_repository.find_template_code_by_site_usage_star(site_type, usage_type, is_star)