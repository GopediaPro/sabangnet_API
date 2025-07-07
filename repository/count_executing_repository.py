from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm.attributes import flag_modified

class CountExecutingRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_and_increment(self, table, count_nm: str) -> int:
        """
        주어진 table(모델)과 count_nm(카운터 이름)로 해당 row의 count_rev 값을 읽고 +1 하여 저장 후, 증가된 값을 반환
        (row가 여러 개라면 count_nm 기준)
        """
        result = await self.session.execute(select(table).where(table.count_nm == count_nm))
        row = result.scalar_one_or_none()
        if row is None:
            # row가 없으면 새로 생성 (초기값 1)
            row = table(count_nm=count_nm, count_rev=1)
            self.session.add(row)
            await self.session.commit()
            return 1
        else:
            current_value = getattr(row, 'count_rev', None)
            if current_value is None:
                setattr(row, 'count_rev', 1)
                await self.session.commit()
                return 1
            setattr(row, 'count_rev', current_value + 1)
            flag_modified(row, 'count_rev')
            await self.session.commit()
            return getattr(row, 'count_rev')
