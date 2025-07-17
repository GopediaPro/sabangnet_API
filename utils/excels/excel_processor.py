"""
Excel 파일 처리를 위한 유틸리티 클래스
Product Registration 데이터 전용 처리기
"""

import json
import pandas as pd
from pathlib import Path
from utils.logs.log_utils import write_log
from typing import List, Dict, Any, Optional
from utils.logs.sabangnet_logger import get_logger


logger = get_logger(__name__)


class ProductRegistrationExcelProcessor:
    """상품 등록 데이터 Excel 처리 전용 클래스"""
    
    def __init__(self):
        self.required_columns = [
            'product_nm', 'goods_nm', 'detail_path_img', 'delv_cost', 
            'goods_search', 'goods_price', 'certno', 'char_process',
            'char_1_nm', 'char_1_val', 'char_2_nm', 'char_2_val',
            'img_path', 'img_path1', 'img_path2', 'img_path3',
            'img_path4', 'img_path5', 'goods_remarks', 'mobile_bn',
            'one_plus_one_bn', 'goods_remarks_url', 'delv_one_plus_one'
        ]
    
    def read_excel_k_to_az_columns(self, file_path: str, sheet_name: str = "Sheet1") -> List[Dict]:
        """
        Excel 파일에서 K:AZ 컬럼 데이터를 읽어옵니다.
        
        Args:
            file_path: Excel 파일 경로
            sheet_name: 시트명 (기본값: Sheet1)
            
        Returns:
            List[Dict]: 처리된 데이터 리스트
        """
        try:
            # Excel 파일 읽기
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            # K(10)부터 AZ(51)까지의 컬럼 선택 (0-based index)
            # K=10, L=11, ..., AZ=51
            k_to_az_columns = df.iloc[:, 10:52]  # K부터 AZ까지
            
            logger.info(f"읽어온 컬럼 수: {len(k_to_az_columns.columns)}")
            logger.info(f"읽어온 행 수: {len(k_to_az_columns)}")
            logger.info(f"읽어온 데이터: {k_to_az_columns}")


            # # 로그 파일로 전체 데이터 debug용 기록
            # try:
            #     write_log(
            #         f"[Excel Data Read] file: {file_path}, sheet: {sheet_name}\n{k_to_az_columns.to_json(force_ascii=False, orient='records', indent=2)}",
            #         log_name="excel_data_read.log"
            #     )
            # except Exception as log_exc:
            #     logger.warning(f"로그 파일 기록 실패: {log_exc}")
            
            # DataFrame을 dict 리스트로 변환
            data_list = k_to_az_columns.to_dict('records')
            
            # 데이터 검증 및 정리
            processed_data = []
            for idx, row in enumerate(data_list):
                try:
                    processed_row = self._process_row_data(row, idx)
                    if processed_row:
                        processed_data.append(processed_row)
                except Exception as e:
                    logger.warning(f"행 {idx} 처리 중 오류: {e}")
                    continue
            
            logger.info(f"처리된 데이터 수: {len(processed_data)}")
            write_log(
                f"[Excel Data Read] file: {file_path}, sheet: {sheet_name}\n{json.dumps(processed_data, ensure_ascii=False, indent=2)}",
                log_name="excel_data_transferred.log"
            )
            return processed_data
            
        except Exception as e:
            logger.error(f"Excel 파일 읽기 실패: {e}")
            raise
    
    def _process_row_data(self, row: Dict, row_index: int) -> Optional[Dict]:
        """
        개별 행 데이터를 처리합니다.
        
        Args:
            row: 원본 행 데이터
            row_index: 행 인덱스
            
        Returns:
            Optional[Dict]: 처리된 행 데이터 또는 None
        """
        # 빈 행 체크 (모든 값이 NaN인 경우)
        if all(pd.isna(value) for value in row.values()):
            return None
        
        processed = {}
        
        # 컬럼 매핑 및 데이터 타입 변환
        # 만약 모두 Unnamed 컬럼이면 ordered mapping 사용
        if all(str(k).startswith("Unnamed:") for k in row.keys()):
            column_mapping = self._get_ordered_column_mapping()
        else:
            column_mapping = self._get_column_mapping()
        
        for excel_col, db_field in column_mapping.items():
            raw_value = row.get(excel_col)
            processed[db_field] = self._convert_value(raw_value, db_field)
        
        return processed
    
    def _get_column_mapping(self) -> Dict[str, str]:
        """
        Excel 컬럼과 DB 필드 매핑을 반환합니다.
        실제 Excel 파일의 컬럼명에 맞게 수정 필요
        """
        return {
            # Excel 컬럼명 -> DB 필드명
            # 실제 Excel 파일 구조에 맞게 수정해야 함
            '제품명': 'product_nm',
            '상품명': 'goods_nm', 
            '상세페이지경로': 'detail_path_img',
            '배송비': 'delv_cost',
            '키워드': 'goods_search',
            '판매가': 'goods_price',
            '인증번호': 'certno',
            '진행옵션': 'char_process',
            '옵션명1': 'char_1_nm',
            '옵션상세1': 'char_1_val',
            '옵션명2': 'char_2_nm',
            '옵션상세2': 'char_2_val',
            '대표이미지': 'img_path',
            '부가이미지1': 'img_path1',
            '부가이미지2': 'img_path2',
            '부가이미지3': 'img_path3',
            '부가이미지4': 'img_path4',
            '부가이미지5': 'img_path5',
            '상세설명': 'goods_remarks',
            '모바일배너': 'mobile_bn',
            '1+1배너': 'one_plus_one_bn',
            '상세설명URL': 'goods_remarks_url',
            '1+1옵션배송': 'delv_one_plus_one'
        }
    
    def _get_ordered_column_mapping(self) -> Dict[str, str]:
        """
        'Unnamed: 10', 'Unnamed: 11', ... 순서대로 self.required_columns에 매핑
        Returns:
            Dict[str, str]: 엑셀 컬럼명(unnamed) -> DB 필드명
        """
        start_idx = 10  # K 컬럼
        mapping = {}
        for i, db_field in enumerate(self.required_columns):
            excel_col = f"Unnamed: {start_idx + i}"
            mapping[excel_col] = db_field
        return mapping
    
    def _convert_value(self, value: Any, field_name: str) -> Any:
        """
        필드별 데이터 타입 변환을 수행합니다.
        
        Args:
            value: 원본 값
            field_name: 필드명
            
        Returns:
            Any: 변환된 값
        """
        # NaN 처리
        if pd.isna(value):
            return None
        
        # Numeric 필드 처리
        numeric_fields = ['delv_cost', 'goods_price']
        if field_name in numeric_fields:
            try:
                return int(float(value)) if value != '' else None
            except (ValueError, TypeError):
                return None
        
        # String 필드 처리 (무조건 str로 변환)
        if value is not None:
            return str(value).strip() if str(value).strip() else None
        
        return value
    
    def validate_data(self, data: List[Dict]) -> tuple[List[Dict], List[str]]:
        """
        데이터 유효성 검증을 수행합니다.
        
        Args:
            data: 검증할 데이터 리스트
            
        Returns:
            tuple: (유효한 데이터 리스트, 오류 메시지 리스트)
        """
        valid_data = []
        errors = []
        
        for idx, row in enumerate(data):
            row_errors = []
            
            # 필수 필드 검증
            required_fields = ['product_nm', 'goods_nm']
            for field in required_fields:
                if not row.get(field):
                    row_errors.append(f"필수 필드 '{field}' 누락")
            
            # 숫자 필드 검증
            numeric_fields = ['delv_cost', 'goods_price']
            for field in numeric_fields:
                value = row.get(field)
                if value is not None:
                    try:
                        int(value)
                    except (ValueError, TypeError):
                        row_errors.append(f"'{field}' 필드는 숫자여야 합니다")
            
            if row_errors:
                errors.append(f"행 {idx + 1}: {', '.join(row_errors)}")
            else:
                valid_data.append(row)
        
        return valid_data, errors


class ExcelExporter:
    """Excel 내보내기 전용 클래스"""
    
    def __init__(self, output_dir: str = "./files/excel"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def export_to_excel(self, data: List[Dict], filename: str, sheet_name: str = "Sheet1") -> str:
        """
        데이터를 Excel 파일로 내보냅니다.
        
        Args:
            data: 내보낼 데이터
            filename: 파일명 (확장자 제외)
            sheet_name: 시트명
            
        Returns:
            str: 저장된 파일 경로
        """
        try:
            df = pd.DataFrame(data)
            file_path = self.output_dir / f"{filename}.xlsx"
            
            df.to_excel(file_path, sheet_name=sheet_name, index=False)
            
            logger.info(f"Excel 파일 저장 완료: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"Excel 파일 저장 실패: {e}")
            raise
