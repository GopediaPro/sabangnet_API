from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from core.db import get_async_session
from services.mall_certification_handling.mall_certification_handling_read_service import MallCertificationHandlingReadService
from schemas.mall_certification_handling.response.mall_certification_handling_response import MallCertificationHandlingResponse
from schemas.mall_certification_handling.request.mall_certification_handling_form import MallCertificationHandlingForm
from services.mall_certification_handling.usecase.mall_certification_detail_usecase import MallCertificationDetailUsecase

router = APIRouter(
    prefix="/mall-certification-handling",
    tags=["mall-certification-handling"],
)

def get_mall_certification_handling_read_service(session: AsyncSession = Depends(get_async_session)) -> MallCertificationHandlingReadService:
    return MallCertificationHandlingReadService(session=session)

def get_mall_certification_detail_usecase(session: AsyncSession = Depends(get_async_session)) -> MallCertificationDetailUsecase:
    return MallCertificationDetailUsecase(session=session)

@router.get("", response_model=List[MallCertificationHandlingResponse])
async def get_mall_certification_handling(
    mall_certification_handling_read_service: MallCertificationHandlingReadService = Depends(get_mall_certification_handling_read_service),
) -> List[MallCertificationHandlingResponse]:
    return [MallCertificationHandlingResponse.from_dto(dto) for dto in await mall_certification_handling_read_service.get_mall_certification_handling_all()]

@router.post("", response_model=MallCertificationHandlingResponse)
async def create_mall_certification_handling(
    request: MallCertificationHandlingForm,
    mall_certification_detail_usecase: MallCertificationDetailUsecase = Depends(get_mall_certification_detail_usecase),
) -> MallCertificationHandlingResponse:
    return MallCertificationHandlingResponse.from_dto(await mall_certification_detail_usecase.create_mall_certification_handling(request=request))