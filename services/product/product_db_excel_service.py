import io
import asyncio
import sys
import os
from pathlib import Path
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession

# 프로젝트 루트 경로를 sys.path에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from repository.product_repository import ProductRepository
from schemas.product.product_raw_data_dto import ProductRawDataDto
from utils.product_create_field_mapping_to_xml import PRODUCT_CREATE_FIELD_MAPPING
from models.product.product_raw_data import ProductRawData
from core.db import get_async_session





class ProductDbExcelService:
    def __init__(
            self,
            session: AsyncSession
        ):
        self.session = session
        self.product_repository = ProductRepository(session)

    
    async def get_product_raw_data_all(self) -> list[ProductRawDataDto]:
        objects = await self.product_repository.get_product_raw_data_all()
        return [ProductRawDataDto.model_validate(obj) for obj in objects]
    

    def convert_db_to_excel(self, dto_list: list[ProductRawDataDto]) -> io.BytesIO:
        dto_ = [dto.model_dump() for dto in dto_list]
            
        print(dto_)

# class DbToExcelConverter:

#     @staticmethod
    
        # df = pd.DataFrame(data)
        # df.columns = [k for k in PRODUCT_CREATE_FIELD_MAPPING.keys()]
        # stream = io.BytesIO()
        # with pd.ExcelWriter(stream, engine='xlsxwriter') as writer:
        #     df.to_excel(writer, index=False, sheet_name='품번코드대량등록툴')
        # stream.seek(0)
    

# class ExcelToDbConverter:

#     @staticmethod
#     def convert_excel_to_db(data: io.BytesIO) -> io.BytesIO:
#         ...


if __name__ == "__main__":
    async def test_session():
        from core.db import AsyncSessionLocal
        async with AsyncSessionLocal() as session:
            product_db_excel_service = ProductDbExcelService(session)
                    
            dto_list: ProductRawDataDto = await product_db_excel_service.get_product_raw_data_all()
            product_db_excel_service.convert_db_to_excel(dto_list)

    asyncio.run(test_session())