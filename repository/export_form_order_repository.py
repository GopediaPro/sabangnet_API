from sqlalchemy import select, delete, func, update, text
from sqlalchemy.ext.asyncio import AsyncSession
from models.order.export_form_order import BaseExportFormOrder
from schemas.order.export_form_order_dto import ExportFormOrderDto

class ExportFormOrderRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_export_form_orders(self, skip: int = None, limit: int = None, template_code: str = None) -> list[BaseExportFormOrder]:
        try:
            query = select(BaseExportFormOrder).order_by(BaseExportFormOrder.id)
            if template_code == 'all':
                pass  # no filter, fetch all
            elif template_code is None or template_code == '':
                query = query.where((BaseExportFormOrder.form_name == None) | (BaseExportFormOrder.form_name == ''))
            else:
                query = query.where(BaseExportFormOrder.form_name == template_code)
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

    async def get_export_form_orders_pagination(self, page: int = 1, page_size: int = 20, template_code: str = None) -> list[BaseExportFormOrder]:
        skip = (page - 1) * page_size
        limit = page_size
        return await self.get_export_form_orders(skip, limit, template_code)

    async def create_export_form_order(self, obj_in: ExportFormOrderDto) -> BaseExportFormOrder:
        obj_in = BaseExportFormOrder(**obj_in.model_dump())
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

    async def bulk_insert(self, objects: list[BaseExportFormOrder]):
        self.session.add_all(objects)
        await self.session.commit()
        return len(objects)

    async def bulk_update(self, objects: list[BaseExportFormOrder]):
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
                stmt = update(BaseExportFormOrder).where(BaseExportFormOrder.idx == idx).values(**values)
                await self.session.execute(stmt)
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
                db_obj = await self.session.get(BaseExportFormOrder, id)
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
            await self.session.execute(delete(BaseExportFormOrder))
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()

    async def delete_duplicate(self):
        try:
            # 중복 제거 쿼리
            stmt = text("""
            DELETE FROM export_form_orders
            WHERE id IN (
                SELECT id FROM (
                    SELECT id,
                        ROW_NUMBER() OVER (
                            PARTITION BY idx
                            ORDER BY updated_at DESC, id DESC
                        ) as row_num
                    FROM export_form_orders
                ) ranked
                WHERE row_num > 1
            )
        """)

            result = await self.session.execute(stmt)
            deleted_count = result.rowcount
            await self.session.commit()

            print(f"중복 제거 완료: {deleted_count}개 행 삭제됨")
            return deleted_count

        except Exception as e:
            await self.session.rollback()
            print(f"중복 제거 실패: {e}")
            raise e

    async def count_all(self, template_code: str = None) -> int:
        try:
            query = select(func.count()).select_from(BaseExportFormOrder)
            if template_code == 'all':
                pass  # no filter, fetch all
            elif template_code is None or template_code == '':
                query = query.where((BaseExportFormOrder.form_name == None) | (BaseExportFormOrder.form_name == ''))
            else:
                query = query.where(BaseExportFormOrder.form_name == template_code)
            result = await self.session.execute(query)
            return result.scalar_one()
        except Exception as e:
            await self.session.rollback()
            raise e
        finally:
            await self.session.close()
