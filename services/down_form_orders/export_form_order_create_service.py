from sqlalchemy.ext.asyncio import AsyncSession
from models.down_form_orders.export_form_order import BaseExportFormOrder
from schemas.down_form_orders.export_form_order_dto import ExportFormOrderDto
from repository.export_form_order_repository import ExportFormOrderRepository


class ExportFormOrderCreateService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.export_form_order_repository = ExportFormOrderRepository(session)    

    async def create_export_form_order(self, idx: str) -> ExportFormOrderDto:
        return await self.export_form_order_repository.create_export_form_order(ExportFormOrderDto(idx=idx))

    async def bulk_create_export_form_orders(self, items: list[ExportFormOrderDto]) -> int:
        orm_objs = [item.to_orm(BaseExportFormOrder) for item in items]
        return await self.export_form_order_repository.bulk_insert(orm_objs)