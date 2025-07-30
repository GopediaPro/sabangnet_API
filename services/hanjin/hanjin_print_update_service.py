from sqlalchemy.ext.asyncio import AsyncSession
from utils.logs.sabangnet_logger import get_logger
from models.hanjin.hanjin_printwbls import HanjinPrintwbls
from services.hanjin.adapter.hanjin_wbls_adapter import HanjinWblsAdapter
from repository.hanjin_printwbls_repository import HanjinPrintwblsRepository


logger = get_logger(__name__)


class HanjinPrintUpdateService(HanjinWblsAdapter):
    def __init__(self, session: AsyncSession = None):
        super().__init__()
        self.printwbls_repo = HanjinPrintwblsRepository(session)

    async def update_with_api_response(self, record_id: int, api_response: dict) -> HanjinPrintwbls:
        return await self.printwbls_repo.update_with_api_response(record_id, api_response)
