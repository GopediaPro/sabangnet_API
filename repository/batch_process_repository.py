from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert
from models.macro_batch_processing.batch_process import BatchProcess
from utils.logs.sabangnet_logger import get_logger

logger = get_logger(__name__)


class BatchProcessRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_batch_process(self, batch_data: dict) -> BatchProcess:
        """새로운 BatchProcess 생성"""
        try:
            query = insert(BatchProcess).returning(BatchProcess)
            result = await self.session.execute(query, [batch_data])
            await self.session.commit()
            
            batch_process = result.scalar_one()
            await self.session.refresh(batch_process)
            
            logger.info(f"BatchProcess 생성 완료: batch_id={batch_process.batch_id}")
            return batch_process
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"BatchProcess 생성 중 오류: {e}")
            raise

    async def get_batch_process_by_id(self, batch_id: int) -> BatchProcess:
        """batch_id로 BatchProcess 조회"""
        try:
            query = select(BatchProcess).where(BatchProcess.batch_id == batch_id)
            result = await self.session.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"BatchProcess 조회 중 오류: {e}")
            raise
