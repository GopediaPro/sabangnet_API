from sqlalchemy.ext.asyncio import AsyncSession

from models.order.down_form_order import BaseDownFormOrder
from schemas.order.down_form_order_dto import DownFormOrderDto
from repository.down_form_order_repository import DownFormOrderRepository


class DownFormOrderReadService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.down_form_order_repository = DownFormOrderRepository(session)

    async def get_down_form_orders(self, skip: int = None, limit: int = None) -> list[DownFormOrderDto]:
        down_form_orders: list[BaseDownFormOrder] = await self.down_form_order_repository.get_down_form_orders(skip, limit)
        return [DownFormOrderDto.model_validate(down_form_order) for down_form_order in down_form_orders]

    async def get_down_form_order_by_idx(self, idx: str) -> DownFormOrderDto:
        return DownFormOrderDto.model_validate(await self.down_form_order_repository.get_down_form_order_by_idx(idx))

    async def get_down_form_orders_paginated(self, page: int = 1, page_size: int = 100, template_code: str = None) -> tuple[list[BaseDownFormOrder], int]:
        items: list[BaseDownFormOrder] = await self.down_form_order_repository.get_down_form_orders_pagination(page, page_size, template_code)
        total: int = await self.down_form_order_repository.count_all(template_code)
        return items, total
    
    async def get_down_form_orders_by_template_code(self, template_code: str) -> list[DownFormOrderDto]:
        """
        get down_form_orders
        returns:
            down_form_orders: down_form_orders SQLAlchemy ORM 인스턴스
        """

        down_form_order_dtos: list[DownFormOrderDto] = []

        down_form_order_models: list[BaseDownFormOrder] = await self.down_form_order_repository.get_down_form_orders_by_template_code(template_code=template_code)
        for down_form_order_model in down_form_order_models:
            down_form_order_dtos.append(DownFormOrderDto.model_validate(down_form_order_model))

        return down_form_order_dtos