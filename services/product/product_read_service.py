import io
import pandas as pd
import urllib.parse
import tempfile
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from fastapi.responses import StreamingResponse

from utils.logs.sabangnet_logger import get_logger
from utils.mappings.product_create_field_db_mapping import PRODUCT_CREATE_FIELD_MAPPING

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.inspection import inspect
from models.product.product_raw_data import ProductRawData
from repository.product_repository import ProductRepository
from schemas.product.product_raw_data_dto import ProductRawDataDto
from utils.exceptions.http_exceptions import DataNotFoundException

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

    # ORM 컬럼 집합
    def _orm_field_set(self) -> set[str]:
        """
        ProductRawData ORM에 실제로 존재하는 컬럼명(lowercase) 집합
        """
        return {c.key.lower() for c in inspect(ProductRawData).mapper.column_attrs}

    # 매핑을 ORM 기준으로 필터링
    def _mapping_keys_and_values(
        self,
        include_derived: bool = False   # 파생 컬럼(my_category/std_category) 포함 여부
    ) -> Tuple[List[str], List[str]]:
        """
        PRODUCT_CREATE_FIELD_MAPPING을
        - 한글 헤더 리스트(mapping_key_list)
        - DB필드명 리스트(mapping_value_list)
        로 분리하되, **ORM에 없는 컬럼은 제외**한다.
        """
        orm_fields = self._orm_field_set()
        derived_allow = {"my_category", "std_category"} if include_derived else set()

        mapping_key_list: List[str] = []
        mapping_value_list: List[str] = []

        for ko_header, db_field_or_tuple in PRODUCT_CREATE_FIELD_MAPPING.items():
            # 값이 튜플(다중 매핑)인 경우 펼쳐서 각각 체크
            if isinstance(db_field_or_tuple, tuple):
                kept_any = False
                for code in db_field_or_tuple:
                    col = code.lower()
                    if col in orm_fields or col in derived_allow:
                        mapping_key_list.append(ko_header)   # 같은 한글 헤더를 반복해서 두면 엑셀 머지가 안되므로
                        mapping_value_list.append(col)
                        kept_any = True
                # 아무 것도 남지 않으면 해당 한글 헤더는 통째로 스킵
                if not kept_any:
                    # skip
                    pass
            else:
                col = db_field_or_tuple.lower()
                if col in orm_fields or col in derived_allow:
                    mapping_key_list.append(ko_header)
                    mapping_value_list.append(col)
                else:
                    # ORM에 없으면 제외
                    pass

        return mapping_key_list, mapping_value_list

    # 카테고리 병합 (파생 컬럼 포함 시에만 수행)
    def _merge_categories(self, rows: List[Dict]) -> None:
        """
        class_cd1~4 를 합쳐 my_category 생성,
        std_category(빈값) 추가,
        기존 class_cd1~4 컬럼 제거.
        rows 는 in-place 로 수정.
        """
        for row in rows:
            parts: List[str] = []
            for i in range(1, 5):
                key = f"class_cd{i}"
                if key in row and row[key]:
                    parts.append(row[key])
                    row.pop(key, None)
            row["std_category"] = ""              # 없던 필드 추가
            row["my_category"] = ">".join(parts)  # 합친 카테고리

    # DataFrame 생성 (파생 컬럼 포함 여부 전달)
    def _build_dataframe(
        self,
        rows: List[Dict],
        include_derived: bool = False
    ) -> pd.DataFrame:
        """
        공통: 매핑(ORM 필터) → (선택)카테고리 병합 → DataFrame 생성
        """
        mapping_key_list, mapping_value_list = self._mapping_keys_and_values(
            include_derived=include_derived
        )

        # 파생 컬럼을 포함하려는 경우에만 카테고리 병합 수행
        if include_derived and (("my_category" in mapping_value_list) or ("std_category" in mapping_value_list)):
            self._merge_categories(rows)

        # DataFrame (순서 보장: mapping_value_list)
        df = pd.DataFrame(rows, columns=mapping_value_list)
        df.columns = mapping_key_list  # 한글 헤더로 교체
        return df
    
    # 대량상품등록(test_product_raw_data) form에 맞춰서 excel 파일 생성
    async def convert_test_product_data_to_excel_file_by_filter(
        self,
        sort_order: Optional[str] = None,
        created_before: Optional[datetime] = None,
        filename: str = "대량상품등록.xlsx",
        sheet_name: str = "상품등록",
    ) -> Tuple[str, str]:
        rows = await self.product_repository.fetch_test_product_raw_data_for_excel(
            sort_order=sort_order,
            created_before=created_before,
        )
        dict_rows: List[Dict] = [self.product_repository.to_dict(r) for r in rows]
        if not dict_rows:
            raise DataNotFoundException("다운로드할 상품 데이터가 없습니다.")

        # df 빌드 (파생 컬럼 제외 옵션)
        df = self._build_dataframe(dict_rows, include_derived=False)

        # 1) 임시 파일에 우선 저장 (xlsxwriter)
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
        tmp_path = tmp.name
        tmp.close()
        with pd.ExcelWriter(tmp_path, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name=sheet_name)

        # 2) openpyxl로 다시 열어 ExcelHandler 스타일 적용
        from openpyxl import load_workbook
        from utils.excels.excel_handler import ExcelHandler  # ★ ExcelHandler 경로에 맞춰 import

        wb = load_workbook(tmp_path)
        ws = wb[sheet_name]

        # 헤더 리스트는 df.columns 사용
        headers = list(df.columns)

        # ExcelHandler 인스턴스 생성(시그니처 유지: (ws, wb))
        excel = ExcelHandler(ws, wb)

        # 헤더 스타일, 열너비/행높이 조정, 줄바꿈 적용
        excel.set_header_style(ws)
        excel._adjust_column_widths(ws, headers)
        excel._adjust_row_heights(ws)
        excel._enable_wrap_text(ws)

        wb.save(tmp_path)

        return tmp_path, filename