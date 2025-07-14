from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from models.order.receive_order import ReceiveOrder
from schemas.order.receive_orders_dto import ReceiveOrdersDto, ReceiveOrdersBulkDto
from repository.receive_orders_repository import ReceiveOrdersRepository


class OrderReadService:
    def __init__(
        self,
        session: AsyncSession,
    ):
        self.receive_orders_repository = ReceiveOrdersRepository(session)

    async def get_order_by_idx(self, idx: str) -> ReceiveOrdersDto:
        return ReceiveOrdersDto.model_validate(await self.receive_orders_repository.get_order_by_idx(idx))

    async def get_orders(self, skip: int = None, limit: int = None) -> ReceiveOrdersBulkDto:
        success_count: int = 0
        error_count: int = 0
        success_idx: list[str] = []
        errors: list[str] = []
        success_data: list[ReceiveOrdersDto] = []

        receive_orders: list[ReceiveOrder] = await self.receive_orders_repository.get_orders(skip, limit)
        for receive_orders in receive_orders:
            try:
                receive_orders_dto = ReceiveOrdersDto.model_validate(receive_orders)
                success_count += 1
                success_idx.append(receive_orders_dto.idx)
                success_data.append(receive_orders_dto)
            except Exception as e:
                error_count += 1
                errors.append(str(e))
                continue
        return ReceiveOrdersBulkDto(
            success_count=success_count,
            error_count=error_count,
            success_idx=success_idx,
            errors=errors,
            success_data=success_data,
        )

    async def get_orders_pagination(self, page: int = 1, page_size: int = 20) -> ReceiveOrdersBulkDto:
        success_count: int = 0
        error_count: int = 0
        success_idx: list[str] = []
        errors: list[str] = []
        success_data: list[ReceiveOrdersDto] = []

        receive_orders = await self.receive_orders_repository.get_orders_pagination(page=page, page_size=page_size)
        for receive_orders in receive_orders:
            try:
                receive_orders_dto = ReceiveOrdersDto.model_validate(receive_orders)
                success_count += 1
                success_idx.append(receive_orders_dto.idx)
                success_data.append(receive_orders_dto)
            except Exception as e:
                error_count += 1
                errors.append(str(e))
                continue
        return ReceiveOrdersBulkDto(
            success_count=success_count,
            error_count=error_count,
            success_idx=success_idx,
            errors=errors,
            success_data=success_data,
        )
    
    async def get_receive_orders_by_filters(self, filters: dict[str, Any]) -> list[ReceiveOrder]:
        return await self.receive_orders_repository.get_receive_orders_by_filters(filters)