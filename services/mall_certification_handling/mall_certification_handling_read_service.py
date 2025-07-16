from typing import List
from core.db import AsyncSession
from repository.mall_certification_handling_repository import MallCertificationHandlingRepository
from schemas.mall_certification_handling.mall_certification_handling_dto import MallCertificationHandlingDto


class MallCertificationHandlingReadService:
    def __init__(self, session: AsyncSession):
        self.mall_authn_handling_repository = MallCertificationHandlingRepository(session)

    async def get_mall_certification_handling_all(self) -> list[MallCertificationHandlingDto]:
        result = await self.mall_authn_handling_repository.find_all()
        mall_certification_handling_dto_list = [MallCertificationHandlingDto.from_model(mall_certification_handling) for mall_certification_handling in result]
        return mall_certification_handling_dto_list

    async def get_mall_certification_handling(self, certification_detail_id: int) -> List[MallCertificationHandlingDto]:
        result = await self.mall_authn_handling_repository.find_by_certification_detail_id(certification_detail_id=certification_detail_id)
        if result is None:
            raise ValueError(f"MallCertificationHandling with certification_detail_id {certification_detail_id} not found")
            
        return [MallCertificationHandlingDto.from_model(mall_certification_handling) for mall_certification_handling in result]