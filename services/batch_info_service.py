from utils.logs.sabangnet_logger import get_logger
from models.batch_process import BatchProcess
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.macros.batch_process_dto import BatchProcessDto
from repository.batch_info_repository import BatchInfoRepository


logger = get_logger(__name__)


class BatchInfoService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.batch_info_repository = BatchInfoRepository(session)

    async def get_batch_info_paginated(self, page: int, page_size: int) -> tuple[list[BatchProcessDto], int]:
        return await self.batch_info_repository.get_batch_info_paginated(page, page_size)
    
    async def save_batch_info(self, batch_dto: BatchProcessDto) -> BatchProcess:
        return await self.batch_info_repository.save_batch_info(batch_dto)
    
    async def build_and_save_batch(self, dto_builder, *args, **kwargs):
        batch_dto = dto_builder(*args, **kwargs)
        return await self.save_batch_info(batch_dto)
    
    async def get_batch_info_latest(self, page: int, page_size: int) -> tuple[list[BatchProcessDto], int]:
        return await self.batch_info_repository.get_batch_info_latest(page, page_size)

async def save_batch_info_service(session: AsyncSession, batch_dto: BatchProcessDto) -> BatchProcess:
    """
    배치 프로세스 정보를 저장하는 서비스 함수
    :param session: 비동기 세션
    :param batch_dto: BatchProcessDto 객체
    :return: 저장된 BatchProcess ORM 객체
    """
    return await BatchInfoRepository(session).save_batch_info(batch_dto)

async def build_and_save_batch(session, dto_builder, *args, **kwargs):
    """
    dto_builder: BatchProcessDto.build_success 또는 build_error 등
    args/kwargs: builder에 전달할 인자
    """
    batch_dto = dto_builder(*args, **kwargs)
    batch_id = None
    try:
        batch_obj = await save_batch_info_service(session, batch_dto)
        batch_id = batch_obj.batch_id
    except Exception as repo_e:
        logger.error(f"batch_info save error: {repo_e}")
    return batch_id 