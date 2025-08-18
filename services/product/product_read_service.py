import io
import pandas as pd
import urllib.parse
from typing import List
from fastapi.responses import StreamingResponse

from utils.logs.sabangnet_logger import get_logger
from utils.mappings.product_create_field_db_mapping import PRODUCT_CREATE_FIELD_MAPPING

from sqlalchemy.ext.asyncio import AsyncSession
from models.product.product_raw_data import ProductRawData
from repository.product_repository import ProductRepository
from schemas.product.product_raw_data_dto import ProductRawDataDto


logger = get_logger(__name__)


class ProductReadService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.product_repository = ProductRepository(session)

    async def get_products_all(self, skip: int, limit: int) -> list[ProductRawDataDto]:
        products = await self.product_repository.get_products_all(skip=skip, limit=limit)
        dtos = [ProductRawDataDto.model_validate(product) for product in products]
        return dtos

    async def get_products_by_pagenation(self, page: int, page_size: int) -> list[ProductRawDataDto]:
        products = await self.product_repository.get_products_by_pagenation(page=page, page_size=page_size)
        dtos = [ProductRawDataDto.model_validate(product) for product in products]
        return dtos

    async def get_product_by_compayny_goods_cd(self, compayny_goods_cd: str) -> ProductRawData:
        return await self.product_repository.find_product_raw_data_by_company_goods_cd(compayny_goods_cd)
    
    async def get_product_by_product_nm_and_gubun(self, product_nm: str, gubun: str) -> ProductRawDataDto:
        res = await self.product_repository.find_product_raw_data_by_product_nm_and_gubun(product_nm, gubun)
        if res is None:
            raise ValueError(f"Product raw data not found: {product_nm}")
        return ProductRawDataDto.model_validate(res)
    
    async def get_product_raw_data_all(self) -> list[ProductRawDataDto]:
        objects = await self.product_repository.get_product_raw_data_all()
        return [ProductRawDataDto.model_validate(obj) for obj in objects]
    
    async def get_product_raw_data_by_company_goods_cds(self, company_goods_cds: List[str]) -> list[ProductRawDataDto]:
        """
        특정 company_goods_cd 목록으로 product_raw_data 조회
        Args:
            company_goods_cds: 조회할 company_goods_cd 목록
        Returns:
            ProductRawDataDto 목록
        """
        objects = await self.product_repository.get_product_raw_data_by_company_goods_cds(company_goods_cds)
        return [ProductRawDataDto.model_validate(obj) for obj in objects]
    
    async def get_product_raw_data_count(self) -> int:
        return await self.product_repository.count_product_raw_data()
    
    async def convert_product_data_to_excel(self) -> StreamingResponse:
        dto_dict_list = await self.get_product_raw_data_all()

        mapping_key_list = []
        mapping_value_list = []
        for k, v in PRODUCT_CREATE_FIELD_MAPPING.items():
            mapping_key_list.append(k)
            if isinstance(v, tuple):
                for code in v:
                    mapping_value_list.append(code.lower())
                continue
            mapping_value_list.append(v.lower())
        
        # class_cd1~4 등을 마이카테고리로 합쳐주는 로직
        category_join_list = []
        for dto_dict in dto_dict_list:
            for dto_k, dto_v in dto_dict.items():
                if "class_cd" in dto_k and dto_v:
                    category_join_list.append(dto_v)
            my_category = ">".join(category_join_list)
            dto_dict["std_category"] = "" # 없던 필드 추가
            dto_dict["my_category"] = my_category
            for i in range(1, 5):
                if f"class_cd{i}" in dto_dict:
                    del dto_dict[f"class_cd{i}"]
        
        # 엑셀 만들기
        df = pd.DataFrame(dto_dict_list, columns=mapping_value_list)
        df.columns = mapping_key_list # 한글 헤더로 바꿈
        stream = io.BytesIO()
        with pd.ExcelWriter(stream, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='품번코드대량등록툴')
        stream.seek(0)

        # 한글 파일명을 URL 인코딩
        filename = "디자인업무일지.xlsx"
        encoded_filename = urllib.parse.quote(filename, safe='')

        return StreamingResponse(
            stream,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"}
        )