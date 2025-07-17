from sqlalchemy.ext.asyncio import AsyncSession
from schemas.mall_certification_handling.request.mall_certification_handling_form import MallCertificationHandlingForm
from services.certification_detail.certification_detail_read_service import CertificationDetailReadService
from services.mall_certification_handling.mall_certification_handling_write_service import MallCertificationHandlingWriteService

class MallCertificationDetailUsecase:
    def __init__(self, session: AsyncSession):
        self.certification_detail_read_service = CertificationDetailReadService(session=session)
        self.mall_certification_handling_write_service = MallCertificationHandlingWriteService(session=session)

    async def create_mall_certification_handling(self, request: MallCertificationHandlingForm):
        certification_detail_dto = await self.certification_detail_read_service.get_certification_detail(certification_detail_id=request.certification_detail_id)
        
        return await self.mall_certification_handling_write_service.create_mall_certification_handling(
            request=request, 
            before_certification_field=certification_detail_dto.certification_field
        )

        

