from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm.attributes import flag_modified

class CountExecutingRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_and_increment(self, table, field: str, id_value: int = 1) -> int:
        """
        주어진 table(모델)과 field(필드명)로 해당 row의 값을 읽고 +1 하여 저장 후, 증가된 값을 반환
        (row가 여러 개라면 id=id_value 기준)
        """
        result = await self.session.execute(select(table).where(table.id == id_value))
        row = result.scalar_one_or_none()
        if row is None:
            # row가 없으면 새로 생성 (초기값 1)
            row = table(id=id_value, **{field: 1})
            self.session.add(row)
            await self.session.commit()
            return 1
        else:
            current_value = getattr(row, field, None)
            if current_value is None:
                setattr(row, field, 1)
                await self.session.commit()
                return 1
            setattr(row, field, current_value + 1)
            # SQLAlchemy가 변경을 인식하도록 flag_modified 호출 (필요시)
            flag_modified(row, field)
            await self.session.commit()
            return getattr(row, field)
