from sqlalchemy.ext.asyncio import AsyncSession
from repository.export_form_order_repository import ExportFormOrderRepository


class ExportFormOrderDeleteService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.export_form_order_repository = ExportFormOrderRepository(session)

    async def bulk_delete_export_form_orders(self, ids: list[int]):
        return await self.export_form_order_repository.bulk_delete(ids)
    
    async def delete_all_export_form_orders(self):
        return await self.export_form_order_repository.delete_all()
    
    async def delete_duplicate_export_form_orders(self):
        return await self.export_form_order_repository.delete_duplicate()