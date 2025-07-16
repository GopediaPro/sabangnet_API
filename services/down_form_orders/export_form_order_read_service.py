from sqlalchemy.ext.asyncio import AsyncSession

from models.down_form_orders.export_form_order import BaseExportFormOrder
from schemas.down_form_orders.export_form_order_dto import ExportFormOrderDto
from repository.export_form_order_repository import ExportFormOrderRepository


class ExportFormOrderReadService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.export_form_order_repository = ExportFormOrderRepository(session)

    async def get_export_form_orders(self, skip: int = None, limit: int = None) -> list[ExportFormOrderDto]:
        down_form_orders: list[ExportFormOrderDto] = await self.export_form_order_repository.get_export_form_orders(skip, limit)
        return [ExportFormOrderDto.model_validate(down_form_order) for down_form_order in down_form_orders]

    async def get_export_form_order_by_idx(self, idx: str) -> ExportFormOrderDto:
        return ExportFormOrderDto.model_validate(await self.export_form_order_repository.get_export_form_order_by_idx(idx))

    async def get_export_form_orders_paginated(
            self, page: int = 1,
            page_size: int = 100,
            template_code: str = None
    ) -> tuple[list[BaseExportFormOrder], int]:
        items: list[BaseExportFormOrder] = await self.export_form_order_repository.get_export_form_orders_pagination(page, page_size, template_code)
        total: int = await self.export_form_order_repository.count_all(template_code)
        return items, total
    
    async def get_export_form_orders_by_template_code(self, template_code: str) -> list[ExportFormOrderDto]:
        down_form_order_dtos: list[ExportFormOrderDto] = []
        down_form_order_models: list[BaseExportFormOrder] = await self.export_form_order_repository.get_export_form_orders_by_template_code(template_code=template_code)
        for down_form_order_model in down_form_order_models:
            down_form_order_dtos.append(ExportFormOrderDto.model_validate(down_form_order_model))

        return down_form_order_dtos
