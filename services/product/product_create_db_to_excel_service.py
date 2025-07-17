import io
import pandas as pd
import urllib.parse

from fastapi.responses import StreamingResponse

from utils.logs.sabangnet_logger import get_logger
from utils.mappings.product_create_field_db_mapping import PRODUCT_CREATE_FIELD_MAPPING

from schemas.product.product_raw_data_dto import ProductRawDataDto


logger = get_logger(__name__)


class ProductDbExcelService:

    @staticmethod
    def convert_db_to_excel(dto_list: list[ProductRawDataDto]) -> StreamingResponse:
        dto_dict_list = [dto.model_dump() for dto in dto_list]

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