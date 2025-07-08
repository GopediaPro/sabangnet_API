from sqlalchemy.ext.asyncio import AsyncSession
from schemas.order.down_form_order_dto import DownFormOrderDto
from services.order.order_read_service import OrderReadService
from services.order.down_form_order_create_service import DownFormOrderCreateService


class DownFormOrderUsecase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.order_read_service = OrderReadService(session)
        self.down_form_order_create_service = DownFormOrderCreateService(session)

    async def create_down_form_order_by_order_idx(self, order_idx: str) -> DownFormOrderDto:
        order_dto = await self.order_read_service.get_order_by_idx(order_idx)
        # 여기에 FLD_DSP 로 구분하는 로직 추가 #
        return await self.down_form_order_create_service.create_down_form_order(order_dto.idx)
