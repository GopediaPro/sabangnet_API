from sqlalchemy.ext.asyncio import AsyncSession
from schemas.order.order_dto import OrderDto, OrderBulkDto
from models.receive_order.receive_order import ReceiveOrder
from repository.receive_order_repository import ReceiveOrderRepository


class OrderReadService:
    def __init__(
        self,
        session: AsyncSession,
    ):
        self.receive_order_repository = ReceiveOrderRepository(session)

    async def get_order_by_idx(self, idx: str) -> OrderDto:
        return OrderDto.model_validate(await self.receive_order_repository.get_order_by_idx(idx))

    async def get_orders(self, skip: int = None, limit: int = None) -> OrderBulkDto:
        success_count: int = 0
        error_count: int = 0
        success_idx: list[str] = []
        errors: list[str] = []
        success_data: list[OrderDto] = []

        orders: list[ReceiveOrder] = await self.receive_order_repository.get_orders(skip, limit)
        for order in orders:
            try:
                order_dto = OrderDto.model_validate(order)
                success_count += 1
                success_idx.append(order_dto.order_id)
                success_data.append(order_dto)
            except Exception as e:
                error_count += 1
                errors.append(str(e))
                continue
        return OrderBulkDto(
            success_count=success_count,
            error_count=error_count,
            success_idx=success_idx,
            errors=errors,
            success_data=success_data,
        )

    async def get_orders_pagination(self, page: int, page_size: int) -> OrderBulkDto:
        success_count: int = 0
        error_count: int = 0
        success_idx: list[str] = []
        errors: list[str] = []
        success_data: list[OrderDto] = []

        orders = await self.receive_order_repository.get_orders_pagination(page, page_size)
        for order in orders:
            try:
                order_dto = OrderDto.model_validate(order)
                success_count += 1
                success_idx.append(order_dto.order_id)
                success_data.append(order_dto)
            except Exception as e:
                error_count += 1
                errors.append(str(e))
                continue
        return OrderBulkDto(
            success_count=success_count,
            error_count=error_count,
            success_idx=success_idx,
            errors=errors,
            success_data=success_data,
        )