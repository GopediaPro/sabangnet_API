import pandas as pd
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from models.down_form_orders.down_form_order import BaseDownFormOrder
from schemas.down_form_orders.down_form_order_dto import DownFormOrderDto


class DownFormOrderConversionService:
    def __init__(self, session: AsyncSession):
        self.session = session

    def convert_orm_to_dto_list(self, down_form_orders: List[BaseDownFormOrder]) -> List[DownFormOrderDto]:
        """
        ORM 객체 리스트를 DownFormOrderDto 리스트로 변환
        
        Args:
            down_form_orders: BaseDownFormOrder ORM 객체 리스트
            
        Returns:
            List[DownFormOrderDto]: 변환된 DTO 리스트
        """
        dto_items = []
        for item in down_form_orders:
            # ORM 객체를 dict로 변환
            item_dict = item.__dict__.copy()
            # _sa_instance_state 제거 (SQLAlchemy 내부 속성)
            item_dict.pop("_sa_instance_state", None)

            # NaN 값을 None으로 변환
            for key, value in item_dict.items():
                if pd.isna(value):
                    item_dict[key] = None

            dto_items.append(DownFormOrderDto.model_validate(item_dict))
        
        return dto_items

    def convert_dto_list_to_dataframe(self, dto_items: List[DownFormOrderDto]) -> pd.DataFrame:
        """
        DownFormOrderDto 리스트를 DataFrame으로 변환하고 데이터 정제
        
        Args:
            dto_items: DownFormOrderDto 리스트
            
        Returns:
            pd.DataFrame: 정제된 DataFrame
        """
        # DataFrame 생성
        data_dict = [dto.model_dump() for dto in dto_items]
        df = pd.DataFrame(data_dict)

        # sale_cnt를 문자열로 강제: "3.0" -> "3", 공백/NaN -> None (엑셀에 빈칸)
        if "sale_cnt" in df.columns:
            df["sale_cnt"] = df["sale_cnt"].map(self._sale_cnt_to_str)

        # tz-aware datetime 컬럼의 timezone 정보 제거
        for col in df.columns:
            if pd.api.types.is_datetime64tz_dtype(df[col]):
                df[col] = df[col].dt.tz_localize(None)
        
        return df

    def _sale_cnt_to_str(self, v):
        """
        sale_cnt 값을 문자열로 변환하는 헬퍼 메서드
        
        Args:
            v: 변환할 값
            
        Returns:
            str or None: 변환된 문자열 또는 None
        """
        if v is None or (isinstance(v, float) and pd.isna(v)):
            return None
        s = str(v).strip()
        if s == "":
            return None
        try:
            return str(int(float(s)))  # "3.0" / Decimal("3") 등도 "3"
        except Exception:
            return s  # 숫자화 불가 시 원 문자열 유지
