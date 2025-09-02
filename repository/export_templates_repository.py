from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.config.export_templates import ExportTemplates
from utils.unicode_utils import normalize_unicode, find_matching_item
import logging

logger = logging.getLogger(__name__)


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
        logger.info(f"Searching template_code with params: site_type='{site_type}', usage_type='{usage_type}', is_star={is_star}")
        
        # 모든 템플릿을 조회한 후 Python에서 비교
        all_templates_query = select(ExportTemplates)
        try:
            all_result = await self.session.execute(all_templates_query)
            all_templates = all_result.scalars().all()
            
            # 유틸리티 함수를 사용하여 매칭되는 템플릿 찾기
            matching_template = find_matching_item(
                [t for t in all_templates if t.is_active],
                site_type=site_type,
                usage_type=usage_type,
                is_star=is_star
            )
            
            if matching_template:
                logger.info(f"Found matching template: {matching_template.template_code}")
                return matching_template.template_code
            
            logger.warning(f"No matching template found for site_type='{site_type}', usage_type='{usage_type}', is_star={is_star}")
            return None
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error in find_template_code_by_site_usage_star: {e}")
            raise e
        finally:
            await self.session.close()

    async def get_template_ids_by_codes(self, template_codes: list[str]) -> list[int]:
        """
        template_code 리스트로 template_id 리스트 조회
        
        Args:
            template_codes: 조회할 template_code 리스트
            
        Returns:
            template_id 리스트
        """
        query = select(ExportTemplates.id).where(
            ExportTemplates.template_code.in_(template_codes),
            ExportTemplates.is_active == True
        )
        
        try:
            result = await self.session.execute(query)
            return [row[0] for row in result.fetchall()]
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Template IDs 조회 실패: {str(e)}")
            raise e
        finally:
            await self.session.close()

    async def get_template_id_by_code(self, template_code: str) -> int:
        query = select(ExportTemplates.id).where(
            ExportTemplates.template_code == template_code,
            ExportTemplates.is_active == True
        )
        result = await self.session.execute(query)
        return result.scalar()