from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.order.down_form_order import BaseDownFormOrder
from schemas.order.down_form_order_dto import DownFormOrderDto
from sqlalchemy import func


class DownFormOrderRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_down_form_order_by_idx(self, idx: str) -> BaseDownFormOrder:
        try:
            query = select(BaseDownFormOrder).where(BaseDownFormOrder.idx == idx)
            result = await self.session.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            await self.session.rollback()
            raise e
        finally:
            await self.session.close()

    async def get_down_form_orders(self, skip: int = None, limit: int = None, template_code: str = None) -> list[BaseDownFormOrder]:
        try:
            query = select(BaseDownFormOrder).order_by(BaseDownFormOrder.id)
            if template_code == 'all':
                pass  # no filter, fetch all
            elif template_code is None or template_code == '':
                query = query.where((BaseDownFormOrder.form_name == None) | (BaseDownFormOrder.form_name == ''))
            else:
                query = query.where(BaseDownFormOrder.form_name == template_code)
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

    async def get_down_form_orders_pagination(self, page: int = 1, page_size: int = 20, template_code: str = None) -> list[BaseDownFormOrder]:
        skip = (page - 1) * page_size
        limit = page_size
        return await self.get_down_form_orders(skip, limit, template_code)

    async def create_down_form_order(self, obj_in: DownFormOrderDto) -> BaseDownFormOrder:
        obj_in = BaseDownFormOrder(**obj_in.model_dump())
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

    async def bulk_insert(self, objects: list[BaseDownFormOrder]):
        self.session.add_all(objects)
        await self.session.commit()
        return len(objects)

    async def bulk_update(self, objects: list[BaseDownFormOrder]):
        try:
            for obj in objects:
                self.session.merge(obj)
            await self.session.commit()
            return len(objects)
        except Exception as e:
            await self.session.rollback()
            raise e
        finally:
            await self.session.close()

    async def bulk_delete(self, ids: list[int]):
        try:
            for id in ids:
                db_obj = await self.session.get(BaseDownFormOrder, id)
                if db_obj:
                    await self.session.delete(db_obj)
            await self.session.commit()
            return len(ids)
        except Exception as e:
            await self.session.rollback()
            raise e
        finally:
            await self.session.close()

    async def count_all(self, template_code: str = None) -> int:
        try:
            query = select(func.count()).select_from(BaseDownFormOrder)
            if template_code == 'all':
                pass  # no filter, fetch all
            elif template_code is None or template_code == '':
                query = query.where((BaseDownFormOrder.form_name == None) | (BaseDownFormOrder.form_name == ''))
            else:
                query = query.where(BaseDownFormOrder.form_name == template_code)
            result = await self.session.execute(query)
            return result.scalar_one()
        except Exception as e:
            await self.session.rollback()
            raise e
        finally:
            await self.session.close()
