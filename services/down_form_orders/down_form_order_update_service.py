from sqlalchemy.ext.asyncio import AsyncSession

from models.down_form_orders.down_form_order import BaseDownFormOrder
from schemas.down_form_orders.down_form_order_dto import DownFormOrderDto
from repository.down_form_order_repository import DownFormOrderRepository


class DownFormOrderUpdateService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.down_form_order_repository = DownFormOrderRepository(session)

    async def bulk_update_down_form_orders(self, items: list[DownFormOrderDto]) -> int:
        orm_objs = [item.to_orm(BaseDownFormOrder) for item in items]
        return await self.down_form_order_repository.bulk_update(orm_objs)
