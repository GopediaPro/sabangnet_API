from sqlalchemy.ext.asyncio import AsyncSession
from utils.logs.sabangnet_logger import get_logger
from repository.batch_info_repository import BatchInfoRepository
from schemas.macro_batch_processing.batch_process_dto import BatchProcessDto


logger = get_logger(__name__)


class BatchInfoReadService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.batch_info_repository = BatchInfoRepository(session)

    async def get_batch_info_paginated(self, page: int, page_size: int) -> tuple[list[BatchProcessDto], int]:
        return await self.batch_info_repository.get_batch_info_paginated(page, page_size)
    
    async def get_batch_info_latest(self, page: int, page_size: int) -> tuple[list[BatchProcessDto], int]:
        return await self.batch_info_repository.get_batch_info_latest(page, page_size)
