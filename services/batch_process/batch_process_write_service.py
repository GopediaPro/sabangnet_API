from sqlalchemy.ext.asyncio import AsyncSession
from repository.batch_process_repository import BatchProcessRepository
from models.macro_batch_processing.batch_process import BatchProcess
from utils.logs.sabangnet_logger import get_logger
from datetime import datetime

logger = get_logger(__name__)


class BatchProcessWriteService:
    def __init__(self, session: AsyncSession):
        self.batch_process_repository = BatchProcessRepository(session)

    async def create_product_mall_value_batch(self, compayny_goods_cd: str, 
                                            gubun: str, created_by: str = "system") -> BatchProcess:
        """ProductMallValue 배치 프로세스 생성 (기본 정보만)"""
        try:
            batch_data = {
                "original_filename": f"{compayny_goods_cd}_product_mall_value_{gubun}",
                "file_name": f"product_mall_value_batch",
                "file_url": "",  # 나중에 업데이트
                "file_size": 0,  # 나중에 업데이트
                "work_status": "PROCESSING",  # 처리 중 상태
                "created_by": created_by,
                "target_table": "product_mall_value",
                "batch_name": f"ProductMallValue_{gubun}_{compayny_goods_cd}",
                "total_records": 0,  # 나중에 업데이트
                "success_records": 0,  # 나중에 업데이트
                "fail_records": 0,  # 나중에 업데이트
                "skip_records": 0
            }
            
            batch_process = await self.batch_process_repository.create_batch_process(batch_data)
            
            logger.info(f"ProductMallValue 배치 프로세스 생성 완료: batch_id={batch_process.batch_id}")
            return batch_process
            
        except Exception as e:
            logger.error(f"ProductMallValue 배치 프로세스 생성 중 오류: {e}")
            raise

    async def update_batch_process_info(self, batch_id: int, xml_url: str, excel_url: str, 
                                      file_size: int, excel_file_size: int,
                                      total_records: int, success_records: int, fail_records: int) -> bool:
        """BatchProcess의 모든 정보 업데이트"""
        try:
            success = await self.batch_process_repository.update_batch_process_info(
                batch_id=batch_id,
                xml_url=xml_url,
                excel_url=excel_url,
                file_size=file_size,
                excel_file_size=excel_file_size,
                total_records=total_records,
                success_records=success_records,
                fail_records=fail_records
            )
            
            if success:
                logger.info(f"BatchProcess 정보 업데이트 완료: batch_id={batch_id}")
            else:
                logger.warning(f"BatchProcess 정보 업데이트 실패: batch_id={batch_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"BatchProcess 정보 업데이트 중 오류: {e}")
            raise
