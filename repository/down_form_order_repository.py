from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from utils.logs.sabangnet_logger import get_logger
from sqlalchemy import select, delete, func, update, text
from models.down_form_orders.down_form_order import BaseDownFormOrder
from schemas.down_form_orders.down_form_order_dto import DownFormOrderDto


logger = get_logger(__name__)


class DownFormOrderRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_down_form_orders(self, skip: int = None, limit: int = None) -> list[BaseDownFormOrder]:
        query = select(BaseDownFormOrder).order_by(BaseDownFormOrder.id.desc())
        if skip is not None:
            query = query.offset(skip)
        if limit is not None:
            query = query.limit(limit)
        result = await self.session.execute(query)
        rows = result.scalars().all()
        return rows
    
    async def get_down_form_order_by_id(self, down_form_order_id: int) -> BaseDownFormOrder:
        try:
            query = select(BaseDownFormOrder).where(BaseDownFormOrder.id == down_form_order_id)
            result = await self.session.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            await self.session.rollback()
            raise e
        finally:
            await self.session.close()

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

    async def get_down_form_orders_by_template_code(self, skip: int = None, limit: int = None, template_code: str = None) -> list[BaseDownFormOrder]:
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
        return await self.get_down_form_orders_by_template_code(skip, limit, template_code)
    
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

    async def bulk_insert(self, objects: list[BaseDownFormOrder]) -> int:
        try:
            self.session.add_all(objects)
            await self.session.commit()
            return len(objects)
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Exception during bulk_insert: {e}")
            raise e
        finally:
            await self.session.close()

    async def bulk_update(self, objects: list[BaseDownFormOrder]) -> int:
        try:
            for obj in objects:
                values = obj.__dict__.copy()
                values.pop('_sa_instance_state', None)
                idx = values.pop('idx', None)
                values.pop('created_at', None)
                values.pop('process_dt', None)
                if idx is None:
                    continue  # idx 없으면 skip
                values['updated_at'] = func.now()
                stmt = update(BaseDownFormOrder).where(BaseDownFormOrder.idx == idx).values(**values)
                await self.session.execute(stmt)
            await self.session.commit()
            return len(objects)
        except Exception as e:
            await self.session.rollback()
            raise e
        finally:
            await self.session.close()

    async def bulk_delete(self, ids: list[int]) -> int:
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

    async def delete_all(self):
        try:
            await self.session.execute(delete(BaseDownFormOrder))
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()

    async def delete_duplicate(self):
        try:
            # 중복 제거 쿼리
            stmt = text("""
            DELETE FROM down_form_orders
            WHERE id IN (
                SELECT id FROM (
                    SELECT id,
                        ROW_NUMBER() OVER (
                            PARTITION BY idx
                            ORDER BY updated_at DESC, id DESC
                        ) as row_num
                    FROM down_form_orders
                ) ranked
                WHERE row_num > 1
            )
        """)

            result = await self.session.execute(stmt)
            deleted_count = result.rowcount
            await self.session.commit()

            logger.info(f"중복 제거 완료: {deleted_count}개 행 삭제됨")
            return deleted_count

        except Exception as e:
            await self.session.rollback()
            logger.error(f"중복 제거 실패: {e}")
            raise e

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

    
    async def save_to_down_form_orders(self, processed_data: list[dict[str, Any]], template_code: str) -> int:
        logger.info(
            f"[START] save_to_down_form_orders | processed_data_count={len(processed_data)} | template_code={template_code}")
        if not processed_data:
            logger.warning("No processed data to save.")
            return 0
        try:
            objects = [BaseDownFormOrder(**row) for row in processed_data]
            self.session.add_all(objects)
            await self.session.commit()
            logger.info(
                f"[END] save_to_down_form_orders | saved_count={len(objects)}")
            return len(objects)
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Exception during save_to_down_form_orders: {e}")
            raise