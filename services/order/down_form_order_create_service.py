from sqlalchemy.ext.asyncio import AsyncSession
from schemas.order.down_form_order_dto import DownFormOrderDto
from repository.down_form_order_repository import DownFormOrderRepository
from models.order.down_form_order import BaseDownFormOrder


class DownFormOrderCreateService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.down_form_order_repository = DownFormOrderRepository(session)

    async def create_down_form_order(self, idx: str) -> DownFormOrderDto:
        return await self.down_form_order_repository.create_down_form_order(DownFormOrderDto(idx=idx))

    async def bulk_create_down_form_orders(self, items: list[DownFormOrderDto]):
        orm_objs = [item.to_orm(BaseDownFormOrder) for item in items]
        return await self.down_form_order_repository.bulk_insert(orm_objs)

    async def bulk_update_down_form_orders(self, items: list[DownFormOrderDto]):
        orm_objs = [item.to_orm(BaseDownFormOrder) for item in items]
        return await self.down_form_order_repository.bulk_update(orm_objs)

    async def bulk_delete_down_form_orders(self, ids: list[int]):
        return await self.down_form_order_repository.bulk_delete(ids)
    
    async def delete_all_down_form_orders(self):
        return await self.down_form_order_repository.delete_all()
    
    async def delete_duplicate_down_form_orders(self):
        return await self.down_form_order_repository.delete_duplicate()