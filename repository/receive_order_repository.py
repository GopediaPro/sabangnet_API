from typing import Optional
from core.db import get_async_session
from models.receive_order.receive_order import ReceiveOrder


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