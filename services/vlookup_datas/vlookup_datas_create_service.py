from sqlalchemy.ext.asyncio import AsyncSession
from repository.vlookup_datas_repository import VlookupDatasRepository
from models.vlookup_datas.vlookup_datas import VlookupDatas
from typing import Any


class VlookupDatasCreateService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.vlookup_datas_repository = VlookupDatasRepository(session)

    async def saved_count_bulk_create_vlookup_datas(self, vlookup_datas: list[dict[str, Any]]) -> dict[str, int]:
        result = await self.vlookup_datas_repository.bulk_create_vlookup_datas(vlookup_datas)
        return {
            "saved_count": len(result),
        }
