from sqlalchemy.ext.asyncio import AsyncSession
from schemas.order.down_form_order_dto import DownFormOrderDto
from repository.down_form_order_repository import DownFormOrderRepository


class DownFormOrderCreateService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.down_form_order_repository = DownFormOrderRepository(session)

    async def create_down_form_order(self, idx: str) -> DownFormOrderDto:
        return await self.down_form_order_repository.create_down_form_order(DownFormOrderDto(idx=idx))

    async def bulk_create_down_form_orders(self, items: list[DownFormOrderDto]):
        objs = [DownFormOrderDto(**item.model_dump()) for item in items]
        return await self.down_form_order_repository.bulk_insert(objs)

    async def bulk_update_down_form_orders(self, items: list[DownFormOrderDto]):
        return await self.down_form_order_repository.bulk_update(items)

    async def bulk_delete_down_form_orders(self, ids: list[int]):
        return await self.down_form_order_repository.bulk_delete(ids)