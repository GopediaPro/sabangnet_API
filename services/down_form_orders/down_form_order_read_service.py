from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession

from models.down_form_orders.down_form_order import BaseDownFormOrder
from schemas.down_form_orders.down_form_order_dto import DownFormOrderDto
from repository.down_form_order_repository import DownFormOrderRepository
from utils.exceptions.down_form_orders_exceptions import DownFormOrderReadServiceException


class DownFormOrderReadService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.down_form_order_repository = DownFormOrderRepository(session)

    async def get_down_form_orders(self, skip: int = None, limit: int = None) -> list[DownFormOrderDto]:
        down_form_orders: list[BaseDownFormOrder] = await self.down_form_order_repository.get_down_form_orders(skip, limit)
        return [DownFormOrderDto.model_validate(down_form_order) for down_form_order in down_form_orders]

    async def get_down_form_order_by_idx(self, idx: str) -> DownFormOrderDto:
        return DownFormOrderDto.model_validate(await self.down_form_order_repository.get_down_form_order_by_idx(idx))

    async def get_down_form_orders_by_pagination(
            self,
            page: int = 1,
            page_size: int = 100,
            template_code: str = None
    ) -> tuple[list[BaseDownFormOrder], int]:
        items: list[BaseDownFormOrder] = (
            await self
            .down_form_order_repository
            .get_down_form_orders_by_pagination(
                page,
                page_size,
                template_code
            )
        )
        total: int = await self.down_form_order_repository.count_all(template_code)
        return items, total
    
    async def get_down_form_orders_by_pagination_with_date_range(
            self,
            date_from: date,
            date_to: date,
            page: int = 1,
            page_size: int = 100,
            template_code: str = "all",
    ) -> tuple[list[BaseDownFormOrder], int]:
        items: list[BaseDownFormOrder] = (
            await self
            .down_form_order_repository
            .get_down_form_orders_by_pagination_with_date_range(
                date_from=date_from,
                date_to=date_to,
                page=page,
                page_size=page_size,
                template_code=template_code
            )
        )
        total: int = await self.down_form_order_repository.count_all(template_code)
        return items, total

    async def get_down_form_orders_by_template_code(self, template_code: str) -> list[DownFormOrderDto]:
        down_form_order_dtos: list[DownFormOrderDto] = []
        down_form_order_models: list[BaseDownFormOrder] = (
            await self.down_form_order_repository.
            get_down_form_orders_by_template_code(template_code=template_code)
        )
        for down_form_order_model in down_form_order_models:
            down_form_order_dtos.append(
                DownFormOrderDto.model_validate(down_form_order_model))

        return down_form_order_dtos

    async def get_down_form_orders_by_work_status(self, work_status: str = None) -> list[BaseDownFormOrder]:
        if  not work_status:
            return await self.down_form_order_repository.get_down_form_orders()
        down_form_order_models: list[BaseDownFormOrder] = await self.down_form_order_repository.get_down_form_orders_by_work_status(work_status=work_status)
        return down_form_order_models
    
    # invoice_no가 없는 주문 데이터 조회
    async def get_orders_without_invoice_no(self, limit: int = 100) -> list[DownFormOrderDto]:
        orders_without_invoice = await self.down_form_order_repository.get_orders_without_invoice_no(limit)
        if not orders_without_invoice:
            raise DownFormOrderReadServiceException("invoice_no가 없는 주문 데이터가 없습니다.")
        return [DownFormOrderDto.model_validate(order) for order in orders_without_invoice]
    
    async def get_down_form_orders_by_date_range(
        self, 
        date_from: date, 
        date_to: date,
        skip: int = None,
        limit: int = None
    ) -> list[BaseDownFormOrder]:
        """
        날짜 범위로 down_form_orders 조회
        
        Args:
            date_from: 시작 날짜
            date_to: 종료 날짜
            skip: 건너뛸 건수 
            limit: 조회할 건수
            
        Returns:
            조회된 주문 데이터 리스트
        """
        return await self.down_form_order_repository.get_down_form_orders_by_date_range(
            date_from, date_to, skip, limit
        )