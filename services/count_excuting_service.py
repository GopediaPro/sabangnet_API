from sqlalchemy.ext.asyncio import AsyncSession
from repository.count_executing_repository import CountExecutingRepository


class CountExecutingService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.count_executing_repository = CountExecutingRepository(session)

    async def get_and_increment(self, table, count_nm: str) -> int:
        return await self.count_executing_repository.get_and_increment(table, count_nm)