from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.order.down_form_order import DownFormOrder
from schemas.order.down_form_order_dto import DownFormOrderDto


class DownFormOrderRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_down_form_order_by_idx(self, idx: str) -> DownFormOrder:
        try:
            query = select(DownFormOrder).where(DownFormOrder.idx == idx)
            result = await self.session.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            await self.session.rollback()
            raise e
        finally:
            await self.session.close()

    async def get_down_form_orders(self, skip: int = None, limit: int = None) -> list[DownFormOrder]:
        try:
            query = select(DownFormOrder).order_by(DownFormOrder.id)
            if skip:
                query = query.offset(skip)
            if limit:
                query = query.limit(limit)

            result = await self.session.execute(query)
            return result.scalars().all()
        except Exception as e:
            await self.session.rollback()
            raise e
        finally:
            await self.session.close()

    async def get_down_form_orders_pagination(self, page: int = 1, page_size: int = 20) -> list[DownFormOrder]:
        skip = (page - 1) * page_size
        limit = page_size
        return await self.get_down_form_orders(skip, limit)

    async def create_down_form_order(self, obj_in: DownFormOrderDto) -> DownFormOrder:
        obj_in = DownFormOrder(**obj_in.model_dump())
        try:
            self.session.add(obj_in)
            await self.session.commit()
            await self.session.refresh(obj_in)
            return obj_in
        except Exception as e:
            await self.session.rollback()
            raise e
        finally:
            await self.session.close()
