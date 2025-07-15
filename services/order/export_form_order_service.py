from sqlalchemy.ext.asyncio import AsyncSession
from repository.export_form_order_repository import ExportFormOrderRepository
from services.order.macros.order_macro_service import run_macro_with_db
from schemas.order.export_form_order_dto import ExportFormOrderDto
from models.order.export_form_order import BaseExportFormOrder

class ExportFormOrderService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.export_form_order_repository = ExportFormOrderRepository(session)

    async def run_macro_with_db(self, template_code: str) -> int:
        return await run_macro_with_db(self.session, template_code)
    
    async def create_export_form_order(self, idx: str) -> ExportFormOrderDto:
        return await self.export_form_order_repository.create_export_form_order(ExportFormOrderDto(idx=idx))

    async def bulk_create_export_form_orders(self, items: list[ExportFormOrderDto]):
        orm_objs = [item.to_orm(BaseExportFormOrder) for item in items]
        return await self.export_form_order_repository.bulk_insert(orm_objs)

    async def bulk_update_export_form_orders(self, items: list[ExportFormOrderDto]):
        orm_objs = [item.to_orm(BaseExportFormOrder) for item in items]
        return await self.export_form_order_repository.bulk_update(orm_objs)

    async def bulk_delete_export_form_orders(self, ids: list[int]):
        return await self.export_form_order_repository.bulk_delete(ids)
    
    async def delete_all_export_form_orders(self):
        return await self.export_form_order_repository.delete_all()
    
    async def delete_duplicate_export_form_orders(self):
        return await self.export_form_order_repository.delete_duplicate()
    
    async def get_export_form_order_by_idx(self, idx: str) -> ExportFormOrderDto:
        return ExportFormOrderDto.model_validate(await self.export_form_order_repository.get_export_form_order_by_idx(idx))

    async def get_export_form_orders_paginated(self, page: int = 1, page_size: int = 100, template_code: str = None):
        items = await self.export_form_order_repository.get_export_form_orders_pagination(page, page_size, template_code)
        total = await self.export_form_order_repository.count_all(template_code)
        return items, total