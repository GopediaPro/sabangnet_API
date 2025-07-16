from sqlalchemy.ext.asyncio import AsyncSession

from repository.down_form_order_repository import DownFormOrderRepository


class DownFormOrderDeleteService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.down_form_order_repository = DownFormOrderRepository(session)

    async def bulk_delete_down_form_orders(self, ids: list[int]):
        return await self.down_form_order_repository.bulk_delete(ids)
    
    async def delete_all_down_form_orders(self):
        return await self.down_form_order_repository.delete_all()
    
    async def delete_duplicate_down_form_orders(self):
        return await self.down_form_order_repository.delete_duplicate()