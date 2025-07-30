from sqlalchemy.ext.asyncio import AsyncSession
from utils.logs.sabangnet_logger import get_logger
from models.hanjin.hanjin_printwbls import HanjinPrintwbls
from services.hanjin.adapter.hanjin_wbls_adapter import HanjinWblsAdapter
from repository.hanjin_printwbls_repository import HanjinPrintwblsRepository
from utils.exceptions.hanjin_wbls_exceptions import HanjinPrintReadServiceException


logger = get_logger(__name__)


class HanjinPrintReadService(HanjinWblsAdapter):
    def __init__(self, session: AsyncSession = None):
        super().__init__()
        self.printwbls_repo = HanjinPrintwblsRepository(session)
    
    async def get_hanjin_printwbls_for_api_request(self, limit: int = 100) -> list[HanjinPrintwbls]:
        records = (
            await self
            .printwbls_repo
            .get_hanjin_printwbls_for_api_request(limit)
        )
        if not records:
            logger.info("API 요청을 위한 데이터가 있는 레코드가 없습니다.")
            raise HanjinPrintReadServiceException("API 요청을 위한 데이터가 있는 레코드가 없습니다.")
        return records
