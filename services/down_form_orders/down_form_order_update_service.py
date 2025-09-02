from typing import Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from models.down_form_orders.down_form_order import BaseDownFormOrder
from repository.down_form_order_repository import DownFormOrderRepository
from schemas.down_form_orders.down_form_order_dto import DownFormOrderDto, DownFormOrdersInvoiceNoUpdateDto
from utils.logs.sabangnet_logger import get_logger

logger = get_logger(__name__)


class DownFormOrderUpdateService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.down_form_order_repository = DownFormOrderRepository(session)

    async def bulk_update_down_form_orders(self, items: list[DownFormOrderDto]) -> int:
        orm_objs = [item.to_orm(BaseDownFormOrder) for item in items]
        return await self.down_form_order_repository.bulk_update(orm_objs)

    async def bulk_update_down_form_order_invoice_no_by_idx(self, idx_invoice_no_dict_list: list[dict[str, str]]) -> list[DownFormOrdersInvoiceNoUpdateDto]:
        return await self.down_form_order_repository.bulk_update_invoice_no_by_idx(idx_invoice_no_dict_list)
    
    async def bulk_upsert_from_excel(self, dto_items: list[DownFormOrderDto]) -> Tuple[int, int]:
        """
        Excel에서 읽어온 데이터를 order_id 기준으로 upsert 처리
        
        Args:
            dto_items: upsert할 DTO 리스트
            
        Returns:
            (inserted_count, updated_count) 튜플
        """
        logger.info(f"Excel upsert 시작 - 총 {len(dto_items)}건")
        
        try:
            inserted_count, updated_count = await self.down_form_order_repository.bulk_upsert(dto_items)
            logger.info(f"Excel upsert 완료 - 삽입: {inserted_count}, 업데이트: {updated_count}")
            return inserted_count, updated_count
        except Exception as e:
            logger.error(f"Excel upsert 실패: {str(e)}")
            raise e