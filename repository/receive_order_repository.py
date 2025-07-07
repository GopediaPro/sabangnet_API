from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.receive_order.receive_order import ReceiveOrder
from sqlalchemy.dialects.postgresql import insert as pg_insert

class ReceiveOrderRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, obj_in: ReceiveOrder) -> ReceiveOrder:
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

    async def get_order_by_idx(self, idx: str) -> ReceiveOrder:
        query = select(ReceiveOrder).where(ReceiveOrder.idx == idx)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_orders(self, skip: int = None, limit: int = None) -> list[ReceiveOrder]:
        """
        주문 데이터 전체 조회
        Args:
            skip: 건너뛸 개수
            limit: 조회할 개수
        Returns:
            ReceiveOrder 리스트
        """
        try:
            stmt = select(ReceiveOrder).order_by(ReceiveOrder.id)
            if skip is not None:
                stmt = stmt.offset(skip)
            if limit is not None:
                stmt = stmt.limit(limit)
            result = await self.session.execute(stmt)
            content = result.scalars().all()
            return content
        except Exception as e:
            await self.session.rollback()
            raise e
        finally:
            await self.session.close()
            
    async def get_orders_pagination(self, page: int = 1, page_size: int = 20) -> list[ReceiveOrder]:
        """
        주문 데이터 페이징 조회
        Args:
            page: 페이지 번호
            page_size: 페이지 당 조회할 개수
        Returns:
            ReceiveOrder 리스트
        """
        try:
            query = select(ReceiveOrder).offset((page - 1) * page_size).limit(page_size).order_by(ReceiveOrder.id)
            result = await self.session.execute(query)
            content = result.scalars().all()
            return content
        except Exception as e:
            await self.session.rollback()
            raise e
        finally:
            await self.session.close()
    
    async def query_create(self, obj_in: dict) -> dict:
        try:
            query = pg_insert(ReceiveOrder).values(obj_in)
            query = query.on_conflict_do_update(index_elements=['idx'], set_=obj_in)
            await self.session.execute(query)
            await self.session.commit()
            return obj_in
        except Exception as e:
            await self.session.rollback()
            raise e
        finally:
            await self.session.close()
