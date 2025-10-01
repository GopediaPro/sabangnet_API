from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update
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

    async def update_batch_process_info(self, batch_id: int, xml_url: str, excel_url: str, 
                                      file_size: int, excel_file_size: int,
                                      total_records: int, success_records: int, fail_records: int) -> bool:
        """BatchProcess의 모든 정보 업데이트"""
        try:
            query = update(BatchProcess).where(
                BatchProcess.batch_id == batch_id
            ).values(
                file_url=xml_url,  # XML URL을 file_url에 저장
                file_size=file_size,  # XML 파일 크기
                work_status="COMPLETED",  # 완료 상태로 변경
                total_records=total_records,
                success_records=success_records,
                fail_records=fail_records,
                skip_records=0
            )
            
            result = await self.session.execute(query)
            await self.session.commit()
            
            if result.rowcount > 0:
                logger.info(f"BatchProcess 정보 업데이트 완료: batch_id={batch_id}")
                return True
            else:
                logger.warning(f"BatchProcess를 찾을 수 없음: batch_id={batch_id}")
                return False
                
        except Exception as e:
            await self.session.rollback()
            logger.error(f"BatchProcess 정보 업데이트 중 오류: {e}")
            raise
