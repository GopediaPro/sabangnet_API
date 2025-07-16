from sqlalchemy.ext.asyncio import AsyncSession
from models.certification_detail.certification_detail import CertificationDetail
from sqlalchemy import select


class CertificationDetailRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_by_id(self, certification_detail_id: int):
        result = await self.session.execute(select(CertificationDetail).where(CertificationDetail.id == certification_detail_id))
        return result.scalars().one_or_none()

    async def find_by_certification_field(self, certification_field: str):
        result = await self.session.execute(select(CertificationDetail).where(CertificationDetail.certification_field == certification_field))
        return result.scalars().all()