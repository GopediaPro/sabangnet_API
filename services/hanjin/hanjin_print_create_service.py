"""
한진 API 운송장 생성 서비스
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from utils.logs.sabangnet_logger import get_logger
from models.hanjin.hanjin_printwbls import HanjinPrintwbls
from schemas.hanjin.hanjin_printWbls_dto import PrintWblsResponse
from models.down_form_orders.down_form_order import BaseDownFormOrder
from schemas.down_form_orders.down_form_order_dto import DownFormOrderDto
from services.hanjin.adapter.hanjin_wbls_adapter import HanjinWblsAdapter
from repository.hanjin_printwbls_repository import HanjinPrintwblsRepository


logger = get_logger(__name__)


class HanjinPrintCreateService(HanjinWblsAdapter):
    """한진 API 운송장 생성 서비스"""
    
    def __init__(self, session: AsyncSession = None):
        super().__init__()
        self.printwbls_repo = HanjinPrintwblsRepository(session)

    async def create_printwbls_from_down_form_orders(self, down_form_order_dtos: list[DownFormOrderDto]) -> list[HanjinPrintwbls]:
        down_form_orders = [
            BaseDownFormOrder(**down_form_order_dto.model_dump()) for down_form_order_dto in down_form_order_dtos
        ]
        created_records: list[HanjinPrintwbls] = (
            await self
            .printwbls_repo
            .create_printwbls_from_down_form_orders(
                down_form_orders
            )
        )
        logger.info(f"down_form_orders에서 {len(created_records)}건의 hanjin_printwbls 레코드 생성 완료")
        return created_records
    
    async def save_printwbls_to_database(
            self, 
            print_response: PrintWblsResponse,
            idx: Optional[str] = None
    ) -> list[HanjinPrintwbls]:
        saved_records = (
            await self
            .printwbls_repo
            .create_multiple_printwbls_records(
                print_response.address_list, 
                idx
            )
        )
        logger.info(f"운송장 출력 결과 {len(saved_records)}건을 데이터베이스에 저장했습니다.")
        return saved_records