from sqlalchemy.ext.asyncio import AsyncSession
from models.mall_certification_handling.mall_certification_handling import MallCertificationHandling
from repository.mall_certification_handling_repository import MallCertificationHandlingRepository
from schemas.mall_certification_handling.mall_certification_handling_dto import MallCertificationHandlingDto
from schemas.mall_certification_handling.request.mall_certification_handling_form import MallCertificationHandlingForm

class MallCertificationHandlingWriteService:
    def __init__(self, session: AsyncSession):
        self.mall_certification_handling_repository = MallCertificationHandlingRepository(session=session)

    async def create_mall_certification_handling(self, request: MallCertificationHandlingForm, before_certification_field: str):
        mall_certification_handling = MallCertificationHandling.builder(
            shop_code=request.shop_code,
            certification_detail_id=request.certification_detail_id,
            before_certification_field=before_certification_field,
            final_certification_field=request.final_certification_field
        )
        model = await self.mall_certification_handling_repository.save(mall_certification_handling=mall_certification_handling)
        return MallCertificationHandlingDto.model_validate(model)