import pandas as pd
from typing import Dict, List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from repository.export_templates_repository import ExportTemplateRepository
from repository.template_column_mapping_repository import TemplateColumnMappingRepository
from utils.logs.sabangnet_logger import get_logger

logger = get_logger(__name__)


class TemplateMappingService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.export_template_repository = ExportTemplateRepository(session)
        self.template_column_mapping_repository = TemplateColumnMappingRepository(session)

    async def get_template_mappings_by_form_names(self, form_names: list[str]) -> dict[int, list[dict]]:
        """
        form_names로부터 template_id를 조회하고, 해당하는 column mappings을 반환
        
        Args:
            form_names: template_code 리스트
            
        Returns:
            template_id별 매핑 정보 딕셔너리
        """
        # 1. form_names로 template_id 조회
        template_ids = await self.export_template_repository.get_template_ids_by_codes(form_names)
        
        if not template_ids:
            return {}
        
        # 2. template_id들로 column mappings 조회
        mappings = await self.template_column_mapping_repository.get_mappings_by_template_ids(template_ids)
        
        # 3. template_id별로 매핑 정보 그룹화
        template_mappings = {}
        for mapping in mappings:
            if mapping.template_id not in template_mappings:
                template_mappings[mapping.template_id] = []
            
            template_mappings[mapping.template_id].append({
                'column_order': mapping.column_order,
                'target_column': mapping.target_column,
                'source_field': mapping.source_field,
                'field_type': mapping.field_type,
                'transform_config': mapping.transform_config or {},
                'aggregation_type': mapping.aggregation_type,
                'description': mapping.description
            })
        
        return template_mappings

    def apply_template_mappings(self, df: pd.DataFrame, template_mappings: dict[int, list[dict]]) -> pd.DataFrame:
        """
        template_mappings에 따라 DataFrame의 컬럼을 동적으로 변환
        
        Args:
            df: 원본 DataFrame
            template_mappings: template_id별 매핑 정보
            
        Returns:
            변환된 DataFrame
        """
        if not template_mappings:
            return df
        
        # 첫 번째 템플릿의 매핑을 기준으로 변환 (여러 템플릿이 있을 경우)
        first_template_id = list(template_mappings.keys())[0]
        mappings = template_mappings[first_template_id]
        # logger.info(f"template_mappings: {template_mappings}")
        # column_order로 정렬
        mappings.sort(key=lambda x: x['column_order'])
        
        # 새로운 컬럼 순서와 매핑 정보 생성
        new_columns = []
        column_mapping = {}
        
        for mapping in mappings:
            target_column = mapping['target_column']
            source_field = mapping['source_field']
            # logger.info(f"first_template_id: {first_template_id}")
            # logger.info(f"df.columns: {df.columns}")
            # logger.info(f"source_field: {source_field}")
            if source_field:
                # 직접 매핑
                if (first_template_id == 27):
                    if (source_field == 'cost'):
                        # form_name에 'smile'이 포함된 경우 pay_cost 사용, 그 외에는 etc_cost 사용
                        df[target_column] = df.apply(
                            lambda row: row['pay_cost'] if 'smile' in str(row['form_name']).lower() else row['etc_cost'], 
                            axis=1
                        )
                        # logger.info(f"source_field=cost: {source_field}")
                        # logger.info(f"df[target_column]: {target_column}")
                    else:
                        df[target_column] = df[source_field]
                        # logger.info(f"source_field: {source_field}")
                        # logger.info(f"df[target_column]: {target_column}")
                else:
                    df[target_column] = df[source_field]
            else:
                df[target_column] = ''

            
            new_columns.append(target_column)
        
        # 컬럼 순서 재정렬
        if new_columns:
            # 기존 컬럼 중 new_columns에 없는 것들은 제거
            existing_columns = [col for col in df.columns if col in new_columns]
            df = df[existing_columns]
            
            # new_columns 순서로 재정렬
            df = df.reindex(columns=new_columns)
        
        return df

    def _apply_formula(self, df: pd.DataFrame, source: str, transform_config: dict) -> pd.Series:
        """
        수식 적용 (간단한 구현)
        
        Args:
            df: DataFrame
            source: 수식 소스
            transform_config: 변환 설정
            
        Returns:
            계산된 Series
        """
        try:
            if source == "convert_name(delivery_method_str)":
                # 배송방법 변환 예시
                return df.get('delivery_method_str', '').map({
                    '선결제': '선결제',
                    '착불': '착불'
                }).fillna('')
            elif source == "mall_won_cost * sale_cnt":
                # 정산예정금액 계산
                mall_won_cost = df.get('mall_won_cost', 0)
                sale_cnt = df.get('sale_cnt', 0)
                return mall_won_cost * sale_cnt
            elif source == "pay_cost - mall_won_cost * sale_cnt":
                # 서비스이용료 계산
                pay_cost = df.get('pay_cost', 0)
                mall_won_cost = df.get('mall_won_cost', 0)
                sale_cnt = df.get('sale_cnt', 0)
                return pay_cost - (mall_won_cost * sale_cnt)
            else:
                # 기본적으로 빈 값 반환
                return pd.Series([''] * len(df))
        except Exception as e:
            logger.error(f"수식 적용 실패: {source}, {str(e)}")
            return pd.Series([''] * len(df))
