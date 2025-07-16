from sqlalchemy.ext.asyncio import AsyncSession
from schemas.certification_detail.certification_detail_dto import CertificationDetailDto
from repository.certification_detail_repository import CertificationDetailRepository

class CertificationDetailReadService:
    def __init__(self, session: AsyncSession):
        self.certification_detail_repository = CertificationDetailRepository(session=session)

    async def get_certification_detail(self, certification_detail_id: int):
        model = await self.certification_detail_repository.find_by_id(certification_detail_id=certification_detail_id)
        if model is None:
            raise ValueError(f"CertificationDetail with id {certification_detail_id} not found")
        return CertificationDetailDto.model_validate(model)

    async def get_certification_detail_by_certification_field(self, certification_field: str):
        model = await self.certification_detail_repository.find_by_certification_field(certification_field=certification_field)
        if model is None:
            raise ValueError(f"CertificationDetail with certification_field {certification_field} not found")
        return CertificationDetailDto.model_validate(model)