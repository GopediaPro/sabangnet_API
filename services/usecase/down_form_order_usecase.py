from schemas.order.order_dto import OrderDto
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.order.down_form_order_dto import DownFormOrderDto
from services.order.order_read_service import OrderReadService
from services.order.down_form_order_create_service import DownFormOrderCreateService


class DownFormOrderUsecase:

    down_form_order_FLD_DSP_FUNCTION_MAPPING: dict[str, str] = {
        '옥션': '',
        '지마켓': '',
        'G마켓': '',
        '브랜디': '',
        '지그재그': '',
        '알리익스프레스': '',
    }

    def __init__(self, session: AsyncSession):
        self.session = session
        self.order_read_service = OrderReadService(session)
        self.down_form_order_create_service = DownFormOrderCreateService(session)

    async def create_down_form_order_by_order_idx(self, idx: str) -> DownFormOrderDto:
        order_dto: OrderDto = await self.order_read_service.get_order_by_idx(idx)
        # 여기에 FLD_DSP 로 구분하는 로직 추가 #
        
        return await self.down_form_order_create_service.create_down_form_order(order_dto.idx)
