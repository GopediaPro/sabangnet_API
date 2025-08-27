import pandas as pd
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from utils.logs.sabangnet_logger import get_logger
logger = get_logger(__name__)

from models.down_form_orders.down_form_order import BaseDownFormOrder
from schemas.down_form_orders.down_form_order_dto import DownFormOrderDto
from services.template_mapping_service import TemplateMappingService


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
        logger.info(f"dto_items: 개수 ({len(dto_items)})")
        
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

        # sale_cnt, expected_payout, service_fee를 문자열로 강제: "3.0" -> "3", 공백/NaN -> None (엑셀에 빈칸)
        numeric_columns = ["sale_cnt", "expected_payout", "service_fee", "pay_cost", "etc_cost"]
        for col in numeric_columns:
            if col in df.columns:
                df[col] = df[col].map(self._numeric_to_str)

        # tz-aware datetime 컬럼의 timezone 정보 제거
        for col in df.columns:
            if pd.api.types.is_datetime64tz_dtype(df[col]):
                df[col] = df[col].dt.tz_localize(None)
        
        return df

    def _numeric_to_str(self, v):
        """
        숫자 값을 문자열로 변환하는 헬퍼 메서드 (sale_cnt, expected_payout, service_fee 등)
        
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

    async def transform_column_by_form_names(self, df: pd.DataFrame, form_names: list[str]) -> pd.DataFrame:
        """
        form_names에 따라 동적으로 컬럼을 변환
        
        Args:
            df: 원본 DataFrame
            form_names: template_code 리스트
            
        Returns:
            pd.DataFrame: 변환된 DataFrame
        """
        if not form_names:
            return df
        
        # TemplateMappingService를 사용하여 동적 매핑 적용
        template_mapping_service = TemplateMappingService(self.session)
        template_mappings = await template_mapping_service.get_template_mappings_by_form_names(form_names)
        
        if template_mappings:
            df = template_mapping_service.apply_template_mappings(df, template_mappings)
        
        return df

    async def get_template_description(self, template_code: str) -> str:
        """
        template_code로부터 export_templates 테이블의 description 조회
        
        Args:
            template_code: 템플릿 코드
            
        Returns:
            str: 템플릿 설명 또는 기본값
        """
        from repository.export_templates_repository import ExportTemplateRepository
        
        export_template_repository = ExportTemplateRepository(self.session)
        
        # 모든 템플릿 조회 후 template_code로 필터링
        all_templates = await export_template_repository.get_export_templates()
        
        for template in all_templates:
            if template.template_code == template_code:
                return template.description or template.template_name or template_code
        
        # 매칭되는 템플릿이 없으면 template_code 반환
        return template_code
