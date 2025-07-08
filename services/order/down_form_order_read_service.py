from sqlalchemy.ext.asyncio import AsyncSession
from schemas.order.down_form_order_dto import DownFormOrderDto
from repository.down_form_order_repository import DownFormOrderRepository


class DownFormOrderReadService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.down_form_order_repository = DownFormOrderRepository(session)

    async def get_down_form_order_by_idx(self, idx: str) -> DownFormOrderDto:
        return DownFormOrderDto.model_validate(await self.down_form_order_repository.get_down_form_order_by_idx(idx))