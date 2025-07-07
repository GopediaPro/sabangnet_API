from typing import Optional
from core.db import get_async_session
from models.receive_order.receive_order import ReceiveOrder
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert

class CreateReceiveOrder:
    async def create(self, obj_in: ReceiveOrder) -> ReceiveOrder:
        session = await get_async_session()
        try:
            session.add(obj_in)
            await session.commit()
            await session.refresh(obj_in)
            return obj_in
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()
    
    async def read_all(self) -> list[ReceiveOrder]:
        session = await get_async_session()
        try: 
            query = select(ReceiveOrder)
            result = await session.execute(query)
            content = result.scalars().all()
            return content
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()

    async def query_create(self, obj_in: dict) -> dict:
        session = await get_async_session()
        try:
            query = pg_insert(ReceiveOrder).values(obj_in)
            query = query.on_conflict_do_update(index_elements=['idx'], set_=obj_in)
            await session.execute(query)
            await session.commit()
            return obj_in
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()