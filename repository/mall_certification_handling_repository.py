from core.db import AsyncSession
from models.mall_certification_handling.mall_certification_handling import MallCertificationHandling
from sqlalchemy import select


class MallCertificationHandlingRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_all(self):
        result = await self.session.execute(select(MallCertificationHandling).order_by(MallCertificationHandling.id))
        return result.scalars().all()

    async def save(self, mall_certification_handling: MallCertificationHandling):
        self.session.add(mall_certification_handling)
        await self.session.commit()
        await self.session.refresh(mall_certification_handling)
        return mall_certification_handling

    async def find_by_certification_detail_id(self, certification_detail_id: int):
        result = await self.session.execute(select(MallCertificationHandling).where(MallCertificationHandling.certification_detail_id == certification_detail_id))
        return result.scalars().all()
        
