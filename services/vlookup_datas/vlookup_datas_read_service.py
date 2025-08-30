from sqlalchemy.ext.asyncio import AsyncSession
from repository.vlookup_datas_repository import VlookupDatasRepository


class VlookupDatasReadService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.vlookup_datas_repository = VlookupDatasRepository(session)
    
    async def get_vlookup_datas_with_not_found_mall_product_ids(self, mall_product_ids: list[str]) -> dict[str, list[dict]]:
        return await self.vlookup_datas_repository.get_vlookup_datas_by_mall_product_ids(mall_product_ids)
        