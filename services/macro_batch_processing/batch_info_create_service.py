from sqlalchemy.ext.asyncio import AsyncSession
from utils.logs.sabangnet_logger import get_logger
from repository.batch_info_repository import BatchInfoRepository
from models.macro_batch_processing.batch_process import BatchProcess
from schemas.macro_batch_processing.batch_process_dto import BatchProcessDto


logger = get_logger(__name__)


class BatchInfoCreateService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.batch_info_repository = BatchInfoRepository(session)

    async def save_batch_info(self, batch_dto: BatchProcessDto) -> BatchProcess:
        """
        배치 프로세스 정보를 저장하는 서비스 함수
        :param session: 비동기 세션
        :param batch_dto: BatchProcessDto 객체
        :return: 저장된 BatchProcess ORM 객체
        """
        return await self.batch_info_repository.save_batch_info(batch_dto)

    async def build_and_save_batch(self, dto_builder, *args, **kwargs):
        """
        dto_builder: BatchProcessDto.build_success 또는 build_error 등
        args/kwargs: builder에 전달할 인자
        """
        batch_dto = dto_builder(*args, **kwargs)
        batch_id = None
        try:
            batch_obj = await self.save_batch_info(batch_dto)
            batch_id = batch_obj.batch_id
        except Exception as repo_e:
            logger.error(f"batch_info save error: {repo_e}")
        return batch_id 