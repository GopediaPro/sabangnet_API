from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.vlookup_datas.vlookup_datas import VlookupDatas
from sqlalchemy.dialects.postgresql import insert


class VlookupDatasRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def bulk_create_vlookup_datas(self, vlookup_datas: list[VlookupDatas]) -> list[VlookupDatas]:
        """vlookup_datas 데이터를 postgres insert (중복 시 무시)"""
        try:
            stmt = insert(VlookupDatas).values(vlookup_datas)
            stmt = stmt.on_conflict_do_nothing(
                index_elements=['mall_product_id'])
            stmt = stmt.returning(VlookupDatas)
            result = await self.session.execute(stmt)
            await self.session.commit()
            return result.scalars().all()
        except Exception as e:
            await self.session.rollback()
            raise e
        finally:
            await self.session.close()

    async def get_vlookup_datas_by_mall_product_ids(self, mall_product_ids: list[str]) -> dict:
        """ mall_product_ids기준으로 조회 및 조회된 데이터와 조회되지 않은 데이터 반환"""
        query = select(VlookupDatas).where(
            VlookupDatas.mall_product_id.in_(mall_product_ids))
        result = await self.session.execute(query)
        items = result.scalars().all()

        found_data: dict[str, dict] = {}
        for item in items:
            found_data[item.mall_product_id] = {
                "mall_product_id": item.mall_product_id,
                "delv_cost": int(item.delv_cost) if item.delv_cost else 0
            }

        not_found_data_ids = list(set(mall_product_ids) - set(found_data.keys()))
        return {
            "found_datas": found_data,
            "not_found_datas": not_found_data_ids
        }
