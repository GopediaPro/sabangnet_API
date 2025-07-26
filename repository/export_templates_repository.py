from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.config.export_templates import ExportTemplates


class ExportTemplateRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_export_templates(self) -> list[ExportTemplates]:
        """
        export template 전체 조회
        Returns:
            list[ExportTemplate]: export template 리스트
        """
        query = select(ExportTemplates)
        try:
            result = await self.session.execute(query)
            return result.scalars().all()
        except Exception as e:
            await self.session.rollback()
            raise e
        finally:
            await self.session.close()