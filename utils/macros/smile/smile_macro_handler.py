import pandas as pd
import openpyxl
from openpyxl.styles import PatternFill
from openpyxl.utils import get_column_letter
from typing import Dict, List, Optional, Tuple
from utils.logs.sabangnet_logger import get_logger
from utils.excels.excel_handler import ExcelHandler
from utils.macros.smile.smile_common_utils import SmileCommonUtils
from repository.smile_erp_data_repository import SmileErpDataRepository
from repository.smile_settlement_data_repository import SmileSettlementDataRepository

logger = get_logger(__name__)


class SmileMacroHandler:
    """
    스마일배송 매크로 핸들러
    VBA 매크로를 Python으로 변환한 처리 로직
    """
    
    def __init__(self, ws, wb=None, erp_repository: Optional[SmileErpDataRepository] = None, 
                 settlement_repository: Optional[SmileSettlementDataRepository] = None):
        self.ws = ws
        self.wb = wb
        self.erp_repository = erp_repository
        self.settlement_repository = settlement_repository
        self.logger = logger
    
    @classmethod
    def from_file(cls, file_path, sheet_index=0, erp_repository=None, settlement_repository=None):
        """
        파일에서 매크로 핸들러 생성
        
        Args:
            file_path: Excel 파일 경로
            sheet_index: 시트 인덱스 (기본값: 0)
            erp_repository: ERP 데이터 리포지토리
            settlement_repository: 정산 데이터 리포지토리
            
        Returns:
            SmileMacroHandler: 매크로 핸들러 인스턴스
        """
        wb = openpyxl.load_workbook(file_path)
        ws = wb.worksheets[sheet_index]
        return cls(ws, wb, erp_repository, settlement_repository)
    
    def save_file(self, file_path):
        """
        파일 저장
        
        Args:
            file_path: 저장할 파일 경로
        """
        if file_path.endswith('_매크로_완료.xlsx'):
            output_path = file_path
        else:
            output_path = file_path.replace('.xlsx', '_매크로_완료.xlsx')
        self.wb.save(output_path)
        return output_path
    
    async def process_stage_1_to_5(self, erp_data: pd.DataFrame, settlement_data: pd.DataFrame):
        """
        1-5단계 처리
        
        Args:
            erp_data: ERP 데이터 DataFrame
            settlement_data: 정산 데이터 DataFrame
            
        Returns:
            bool: 처리 성공 여부
        """
        try:
            self._stage_1_basic_formatting()
            await self._stage_2_erp_matching(erp_data, settlement_data)
            self._stage_3_delete_colored_rows()
            self._stage_4_delete_conditioned_rows()
            self._stage_5_final_processing()
            return True
        except Exception as e:
            self.logger.error(f"1-5단계 처리 중 오류: {str(e)}")
            return False
    
    def process_stage_6_to_8(self, sku_data: pd.DataFrame):
        """
        6-8단계 처리
        
        Args:
            sku_data: SKU 데이터 DataFrame
            
        Returns:
            bool: 처리 성공 여부
        """
        try:
            self._stage_6_sku_processing(sku_data)
            self._stage_7_column_copy_and_format()
            self._stage_8_filter_and_sort()
            return True
        except Exception as e:
            self.logger.error(f"6-8단계 처리 중 오류: {str(e)}")
            return False
    
    def _stage_1_basic_formatting(self):
        """1단계: 기본 서식 처리"""
        # 공통 유틸리티 사용
        SmileCommonUtils.apply_basic_formatting(self.ws, font_size=9, row_height=15)
        SmileCommonUtils.delete_colored_rows(self.ws)
        
        # H열 자동 맞춤
        self.ws.column_dimensions['H'].auto_size = True
    
    async def _stage_2_erp_matching(self, erp_data: pd.DataFrame, settlement_data: pd.DataFrame):
        """2단계: I, J열 삽입 및 ERP 매칭"""
        # I, J열 삽입
        SmileCommonUtils.insert_columns(self.ws, 9, 2, ["ERP매칭", "정산여부"])
        
        # ERP 매칭 및 정산 여부 확인
        x_count = 0
        erp_count = 0
        settlement_count = 0
        
        for row_num in range(2, self.ws.max_row + 1):
            user_id = self.ws[f'A{row_num}'].value
            order_num = self.ws[f'H{row_num}'].value
            
            if order_num and user_id:
                # 데이터베이스에서 ERP 값과 정산 여부 조회
                erp_value = await self._find_erp_value(order_num)
                settlement_value = await self._check_settlement(order_num)
                self.logger.info(f"행 {row_num} (사용자ID: {user_id}): ERP='{erp_value}', 정산='{settlement_value}', 주문번호='{order_num}'")
            else:
                erp_value = ""
                settlement_value = "X"
            
            # ERP 매칭 결과 설정
            self.ws[f'I{row_num}'].value = erp_value
            self.ws[f'J{row_num}'].value = settlement_value
            
            # 디버깅: ERP 값 확인 (처음 10행만)
            if row_num <= 10:
                self.logger.info(f"행 {row_num} ERP 값: '{erp_value}'")
            
            # 카운트
            if erp_value == "X":
                x_count += 1
            elif erp_value:
                erp_count += 1
            
            if settlement_value == "정산":
                settlement_count += 1
        
        self.logger.info(f"ERP 매칭 결과 - X: {x_count}건, ERP: {erp_count}건, 정산: {settlement_count}건")
    
    def _stage_3_delete_colored_rows(self):
        """3단계: 색이 있는 행 삭제"""
        # 공통 유틸리티를 사용하여 색이 있는 행 삭제
        SmileCommonUtils.delete_colored_rows(self.ws)
        self.logger.info("3단계: 색이 있는 행 삭제 완료")
    
    def _stage_4_delete_conditioned_rows(self):
        """4단계: 특정 조건 행 삭제"""
        rows_to_delete = []
        for row_num in range(2, self.ws.max_row + 1):
            erp_match = self.ws[f'I{row_num}'].value
            settlement = self.ws[f'J{row_num}'].value
            
            # 더 구체적인 조건으로 수정
            # ERP 매칭이 되고 정산이 완료된 경우만 삭제
            if erp_match == "ERP" and settlement == "정산":
                rows_to_delete.append(row_num)
                self.logger.info(f"행 {row_num}: ERP=ERP, 정산=정산 (삭제 대상)")
            # ERP 매칭이 안되고 정산도 안된 경우는 보존 (데이터 검증 필요)
            elif erp_match == "X" and settlement == "X":
                self.logger.info(f"행 {row_num}: ERP=X, 정산=X (검증 필요 - 보존)")
        
        # 삭제될 행 수 로깅
        self.logger.info(f"4단계에서 삭제될 행 수: {len(rows_to_delete)} / 총 {self.ws.max_row - 1} 행")
        
        # 역순으로 삭제
        for row_num in reversed(rows_to_delete):
            self.ws.delete_rows(row_num)
        
        self.logger.info(f"4단계 처리 후 남은 행 수: {self.ws.max_row - 1}")
    
    def _stage_5_final_processing(self):
        """5단계: 최종 처리"""
        # I, J열 삭제 (ERP매칭, 정산여부 열 삭제)
        SmileCommonUtils.delete_columns(self.ws, 9, 2)
        
        # D열 오른쪽에 새 E열 삽입
        SmileCommonUtils.insert_columns(self.ws, 5, 1)
        
        # E1 셀에 노란색 배경
        SmileCommonUtils.set_cell_background(self.ws, "E1", "FFFF00")
        
        # B열(정산예정금) + C열(서비스 이용료) 더한 값 계산하여 E열에 입력
        # 정산예정금과 서비스 이용료의 합계를 계산
        self.logger.info("5단계: B열(정산예정금) + C열(서비스 이용료) 합계 계산 시작")
        
        # 디버깅: 처음 몇 행의 B, C열 값 확인
        for row_num in range(2, min(7, self.ws.max_row + 1)):
            b_value = self.ws[f'B{row_num}'].value
            c_value = self.ws[f'C{row_num}'].value
            self.logger.info(f"행 {row_num}: B열={b_value}({type(b_value)}), C열={c_value}({type(c_value)})")
        
        SmileCommonUtils.calculate_sum_formula(self.ws, "E", ["B", "C"], 2)
        self.logger.info("5단계: 합계 계산 완료")
    
    def _stage_6_sku_processing(self, sku_data: pd.DataFrame):
        """6단계: SKU 분해 및 모델명 조합"""
        # AA 뒤에 AB, AC, AD 추가
        SmileCommonUtils.insert_columns(self.ws, 28, 3)
        
        # AD 뒤에 AE 열 추가
        SmileCommonUtils.insert_columns(self.ws, 31, 1, ["모델명+수량"])
        
        # SKU 데이터를 딕셔너리로 변환
        sku_dict = SmileCommonUtils.create_sku_dictionary(sku_data)
        
        # AA 분해 및 모델명 조합
        for row_num in range(2, self.ws.max_row + 1):
            aa_value = self.ws[f'AA{row_num}'].value
            if not aa_value:
                continue
            
            result_text = ""
            aa_str = str(aa_value)
            
            if " " in aa_str:
                text_parts = aa_str.split(" ")
                
                # 첫 번째 부분 처리
                if "/" in text_parts[0]:
                    sku_parts1 = text_parts[0].split("/")
                    self.ws[f'AA{row_num}'].value = sku_parts1[0].strip()
                    self.ws[f'AB{row_num}'].value = sku_parts1[1].strip()
                
                # 두 번째 부분 처리
                if len(text_parts) > 1 and "/" in text_parts[1]:
                    sku_parts2 = text_parts[1].split("/")
                    self.ws[f'AC{row_num}'].value = sku_parts2[0].strip()
                    self.ws[f'AD{row_num}'].value = sku_parts2[1].strip()
            
            # 모델명 조합
            sku1 = str(self.ws[f'AA{row_num}'].value or "").strip()
            qty1 = str(self.ws[f'AB{row_num}'].value or "").strip()
            sku2 = str(self.ws[f'AC{row_num}'].value or "").strip()
            qty2 = str(self.ws[f'AD{row_num}'].value or "").strip()
            
            if sku1 and sku1 in sku_dict:
                model1 = sku_dict[sku1]
                if qty1 and qty1 != "1개":
                    model1 = f"{model1} {qty1}"
                result_text = model1
            
            if sku2 and sku2 in sku_dict:
                model2 = sku_dict[sku2]
                if qty2 and qty2 != "1개":
                    model2 = f"{model2} {qty2}"
                if result_text:
                    result_text = f"{result_text} + {model2}"
                else:
                    result_text = model2
            
            self.ws[f'AE{row_num}'].value = result_text
    
    def _stage_7_column_copy_and_format(self):
        """7단계: 열 복사 및 서식"""
        # K열 뒤에 L열 삽입
        SmileCommonUtils.insert_columns(self.ws, 12, 1)
        
        # AF열 → L열로 복사
        SmileCommonUtils.copy_column_values(self.ws, "AF", "L")
        
        # L1 셀 노란색 배경
        SmileCommonUtils.set_cell_background(self.ws, "L1", "FFFF00")
    
    def _stage_8_filter_and_sort(self):
        """8단계: 필터 및 정렬"""
        # 전체 필터 적용
        SmileCommonUtils.apply_auto_filter(self.ws)
        
        # 정렬: A → S (A기준 정렬)
        # 데이터를 DataFrame으로 변환하여 정렬
        data = []
        headers = []
        
        for row in self.ws.iter_rows(values_only=True):
            if not headers:
                headers = row
            else:
                data.append(row)
        
        df = pd.DataFrame(data, columns=headers)
        df_sorted = SmileCommonUtils.sort_dataframe(df, [headers[0], headers[18]], [True, True])  # A, S 컬럼
        
        # 정렬된 데이터를 다시 워크시트에 쓰기
        for row_idx, row_data in enumerate(df_sorted.values, start=2):
            for col_idx, value in enumerate(row_data, start=1):
                self.ws.cell(row=row_idx, column=col_idx, value=value)
    
    async def _find_erp_value(self, order_no: str) -> str:
        """데이터베이스에서 ERP 값 찾기"""
        try:
            if not self.erp_repository:
                self.logger.warning("ERP 리포지토리가 설정되지 않았습니다. 빈 문자열을 반환합니다.")
                return ""
            
            # Excel에서 읽은 값이 숫자일 수 있으므로 문자열로 변환
            order_no_str = str(order_no) if order_no is not None else ""
            
            self.logger.debug(f"ERP 조회: 주문번호='{order_no_str}' (원본: '{order_no}')")
            
            erp_data = await self.erp_repository.get_erp_data_by_order_number(order_no_str)
            if erp_data and erp_data.erp_code:
                self.logger.debug(f"ERP 데이터 찾음: 주문번호='{order_no_str}' -> ERP코드='{erp_data.erp_code}'")
                return erp_data.erp_code
            else:
                self.logger.debug(f"ERP 데이터 없음: 주문번호='{order_no_str}'")
                return "X"
        except Exception as e:
            self.logger.error(f"ERP 값 조회 중 오류: {str(e)}")
            return ""
    
    async def _check_settlement(self, order_no: str) -> str:
        """데이터베이스에서 정산 여부 확인"""
        try:
            if not self.settlement_repository:
                self.logger.warning("정산 리포지토리가 설정되지 않았습니다. 'X'를 반환합니다.")
                return "X"
            
            # Excel에서 읽은 값이 숫자일 수 있으므로 문자열로 변환
            order_no_str = str(order_no) if order_no is not None else ""
            
            settlement_data_list = await self.settlement_repository.get_settlement_data_by_order_number(order_no_str)
            if settlement_data_list:
                return "정산"
            return "X"
        except Exception as e:
            self.logger.error(f"정산 여부 확인 중 오류: {str(e)}")
            return "X" 