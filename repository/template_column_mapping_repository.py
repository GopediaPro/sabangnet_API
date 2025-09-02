from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.config.template_column_mappings import TemplateColumnMappings
import logging

logger = logging.getLogger(__name__)


class TemplateColumnMappingRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_mappings_by_template_ids(self, template_ids: list[int]) -> list[TemplateColumnMappings]:
        """
        template_id 리스트로 column mappings 조회
        
        Args:
            template_ids: 조회할 template_id 리스트
            
        Returns:
            TemplateColumnMappings 리스트
        """
        query = select(TemplateColumnMappings).where(
            TemplateColumnMappings.template_id.in_(template_ids),
            TemplateColumnMappings.is_active == True
        ).order_by(TemplateColumnMappings.template_id, TemplateColumnMappings.column_order)
        
        try:
            result = await self.session.execute(query)
            return result.scalars().all()
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Template column mappings 조회 실패: {str(e)}")
            raise e
        finally:
            await self.session.close()

    async def get_mappings_by_template_id(self, template_id: int) -> list[TemplateColumnMappings]:
        """
        template_id로 column mappings 조회
        """
        query = select(TemplateColumnMappings).where(
            TemplateColumnMappings.template_id == template_id,
            TemplateColumnMappings.is_active == True
        ).order_by(TemplateColumnMappings.template_id, TemplateColumnMappings.column_order)
        
        try:
            result = await self.session.execute(query)
            mappings = result.scalars().all()
            
            if not mappings:
                error_msg = f"Template ID {template_id}에 대한 column mappings를 찾을 수 없습니다."
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            return mappings
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Template column mappings 조회 실패: {str(e)}")
            raise e
        finally:
            await self.session.close()

    async def get_mappings_all(self) -> list[TemplateColumnMappings]:
        """
        template_id 전체 조회
        """
        query = select(TemplateColumnMappings).where(
            TemplateColumnMappings.is_active == True
        ).order_by(TemplateColumnMappings.template_id, TemplateColumnMappings.column_order)
        result = await self.session.execute(query)
        return result.scalars().all()