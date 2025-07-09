"""브랜디 합포장 자동화 모듈"""

from __future__ import annotations
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet

from utils.excel_handler import ExcelHandler


# 설정 상수
MALL_NAME = "브랜디"
OUTPUT_PREFIX = "브랜디_합포장_자동화_"
RED_FONT = Font(color="FF0000", bold=True)
FONT_MALGUN = Font(name="맑은 고딕", size=9)
HDR_FILL = PatternFill(start_color="006100",
                       end_color="006100", fill_type="solid")
BLUE_FILL = PatternFill(start_color="CCE8FF", end_color="CCE8FF", fill_type="solid")
NO_BORDER = Border()
MULTI_SEP_RE = re.compile(r"[\/;]")

def to_num(val):
    """쉼표·원화기호 등을 제거하고 float 변환 (실패 시 0)."""
    try:
        return float(re.sub(r"[^\d.-]", "", str(val))) if str(val).strip() else 0
    except ValueError:
        return 0


class BrandyProductProcessor:
    """브랜디 상품 정보 처리 유틸리티"""
    
    @staticmethod
    def clean_product_text(txt: str | None) -> str:
        """
        🔄 ExcelHandler 후보
        상품명 문자열 정리 (' 1개' 제거)
        """
        return str(txt or "").replace(" 1개", "").strip()


class BrandyPhoneFormatter:
    """브랜디 전화번호 처리 유틸리티"""
    
    @staticmethod
    def format_phone(val: str | None) -> str:
        """전화번호 포맷팅 (01012345678 → 010-1234-5678)"""
        if not val:
            return ""
        digits = re.sub(r"\D", "", str(val))
        if len(digits) == 11:
            return f"{digits[:3]}-{digits[3:7]}-{digits[7:]}"
        return str(val)


class BrandyOrderMerger:
    """브랜디 주문 데이터 그룹핑 및 병합 처리"""
    
    def __init__(self, ws: Worksheet):
        self.ws = ws
        self.groups = defaultdict(list)
        
    def group_by_product_and_receiver(self) -> None:
        """C열(상품번호)와 J열(수령인) 기준으로 그룹핑"""
        for row in range(2, self.ws.max_row + 1):
            key = (
                f"{str(self.ws[f'C{row}'].value).strip()}"
                f"|{str(self.ws[f'J{row}'].value).strip()}"
            )
            self.groups[key].append(row)
            
    def merge_rows(self) -> List[int]:
        """그룹별 데이터 병합 처리"""
        rows_to_delete = []
        
        for rows in self.groups.values():
            if len(rows) == 1:  # 중복 없음
                continue
                
            base_row = rows[0]  # 첫 행 유지
            
            # D열 금액 합산
            total_d = 0.0
            for row in rows:
                cell_val = self.ws[f"D{row}"].value
                if isinstance(cell_val, str) and cell_val.startswith("="):
                    # 수식이 있는 경우 O+P+V 각각 계산
                    o_val = float(self.ws[f"O{row}"].value or 0)
                    p_val = float(self.ws[f"P{row}"].value or 0)
                    v_val = float(self.ws[f"V{row}"].value or 0)
                    total_d += (o_val + p_val + v_val)
                else:
                    total_d += float(cell_val or 0)
            self.ws[f"D{base_row}"].value = total_d
            
            # G열 수량 합산
            total_g = 0
            for row in rows:
                g_val = self.ws[f"G{row}"].value
                if g_val is not None:
                    try:
                        total_g += float(str(g_val).strip() or 0)
                    except ValueError:
                        pass  # 숫자로 변환할 수 없는 경우 무시
            self.ws[f"G{base_row}"].value = total_g
            
            # F열 모델명 결합
            models = []
            for row in rows:
                model = self.ws[f"F{row}"].value
                if model:
                    clean_model = BrandyProductProcessor.clean_product_text(model)
                    if clean_model:
                        models.append(clean_model)
            self.ws[f"F{base_row}"].value = " + ".join(models)
            
            # 나머지 행은 삭제 대상으로 표시
            rows_to_delete.extend(rows[1:])
            
        return sorted(rows_to_delete, reverse=True)  # 역순 정렬(삭제용)

class BrandySheetProcessor:
    """브랜디 시트 분리 및 자동화 로직 적용"""
    
    def __init__(self, ws: Worksheet):
        self.ws = ws
        self.last_row = ws.max_row
        self.last_col = ws.max_column
        
        # 열 너비 저장
        self.col_widths = [
            ws.column_dimensions[get_column_letter(c)].width
            for c in range(1, self.last_col + 1)
        ]

    def create_empty_sheet(self, wb: Worksheet, sheet_name: str) -> Worksheet:
        """빈 시트 생성 (헤더와 열 너비만 복사)"""
        if sheet_name in wb.sheetnames:
            del wb[sheet_name]
            
        new_ws = wb.create_sheet(sheet_name)
        
        # 헤더와 열 너비 복사
        for c in range(1, self.last_col + 1):
            new_ws.cell(row=1, column=c, 
                       value=self.ws.cell(row=1, column=c).value)
            new_ws.column_dimensions[get_column_letter(c)].width = self.col_widths[c - 1]
            
        return new_ws

    def copy_sheet_data(self, ws: Worksheet) -> None:
        """시트에 데이터 행 복사"""
        for r in range(2, self.last_row + 1):
            for c in range(1, self.last_col + 1):
                ws.cell(row=r, column=c, 
                       value=self.ws.cell(row=r, column=c).value)
            ws[f"A{r}"].value = "=ROW()-1"

    def apply_automation_logic(self, ws: Worksheet) -> None:
        """자동화 로직 적용"""
        # 1. 기본 서식 적용
        ex = ExcelHandler(ws)
        ex.set_basic_format()
        
        # 2. C열(수취인) 기준 정렬
        ex.sort_by_columns([3])
        
        # 3. 그룹핑 및 병합
        merger = BrandyOrderMerger(ws)
        merger.group_by_product_and_receiver()
        rows_to_delete = merger.merge_rows()
        
        # 중복 행 삭제 (역순으로)
        for row_idx in rows_to_delete:
            ws.delete_rows(row_idx)
        
        # 4. D열 수식 재설정
        ex.autofill_d_column(formula="=O{row}+P{row}+V{row}")

        # 5. A열 순번 재설정
        ex.set_row_number(ws)
        
        # 6. 전화번호 처리 (H열, I열)
        for row in range(2, self.last_row + 1):
            for col in ('H', 'I'):
                cell_value = ws[f'{col}{row}'].value
                ws[f'{col}{row}'].value = ex.format_phone_number(cell_value)
        
        # 7. 제주도 주문 처리
        for row in range(2, self.last_row + 1):
            j_value = ws[f'J{row}'].value
            if j_value and "제주" in str(j_value):
                ex.process_jeju_address(row)

        # 8. 문자열→숫자 변환 
        ex.convert_numeric_strings(cols=("P", "W"))      # 텍스트 서식

        # 9. 열 정렬
        ex.set_column_alignment()
        
        # 10. 배경·테두리 제거
        ex.clear_fills_from_second_row()
        ex.clear_borders()

    def copy_to_new_sheet(self, 
                         wb: Worksheet, 
                         sheet_name: str,
                         ex: ExcelHandler) -> None:
        """새 시트 생성 및 자동화 로직 적용"""
        new_ws = self.create_empty_sheet(wb, sheet_name)
        self.copy_sheet_data(new_ws)
        self.apply_automation_logic(new_ws)  # ex 인자 제거

def brandy_merge_packaging(input_path: str) -> str:
    """브랜디 주문 합포장 자동화 처리"""
    # Excel 파일 로드
    ex = ExcelHandler.from_file(input_path)
    
    # 첫 번째 시트에 자동화 로직 적용
    source_ws = ex.ws
    splitter = BrandySheetProcessor(source_ws)
    splitter.apply_automation_logic(source_ws)
    print(f"◼︎ [{MALL_NAME}] 자동화 처리 완료")
    
    # 저장
    output_path = str(
        Path(input_path).with_name(OUTPUT_PREFIX + Path(input_path).name)
    )
    ex.wb.save(output_path)
    ex.wb.close()
    
    print(f"◼︎ [{MALL_NAME}] 합포장 자동화 완료!")
    return output_path


if __name__ == "__main__":
    test_path = "/Users/smith/Documents/github/OKMart/sabangnet_API/files/test-[기본양식]-합포장용.xlsx"
    brandy_merge_packaging(test_path)