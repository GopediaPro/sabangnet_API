"""지그재그 합포장 자동화 모듈"""

from __future__ import annotations
import re
from pathlib import Path
from typing import Dict

from openpyxl.styles import Font, PatternFill, Border
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet
from utils.excel_handler import ExcelHandler


# 설정 상수
MALL_NAME = "지그재그"
BLUE_FILL = PatternFill(start_color="CCE8FF", end_color="CCE8FF", fill_type="solid")


FONT_MALGUN = Font(name="맑은 고딕", size=9)
HDR_FILL = PatternFill(start_color="006100", end_color="006100", fill_type="solid")
NO_BORDER = Border()

STAR_QTY_RE = re.compile(r"\* ?(\d+)")
MULTI_SEP_RE = re.compile(r"[\/;]")


def to_num(val) -> float:
    try:
        return float(re.sub(r"[^\d.-]", "", str(val))) if str(val).strip() else 0.0
    except ValueError:
        return 0.0


class DataCleanerUtils:
    @staticmethod
    def clean_product_text(txt: str | None) -> str:
        """
        🔄 ExcelHandler 후보
        상품명 문자열 정리 - ' 1개' 제거
        """
        return str(txt).replace(" 1개", "").strip() if txt else ""

    @staticmethod
    def build_lookup_map(ws_lookup: Worksheet) -> Dict[str, str]:
        """
        Sheet1의 A:B를 딕셔너리로 변환
        (M열 → V열 매핑용 VLOOKUP 대체)
        """
        return {
            str(r[0]): r[1]
            for r in ws_lookup.iter_rows(min_row=2, max_col=2, values_only=True)
            if r[0] is not None
        }


def convert_m_column_to_int(ws: Worksheet) -> None:
    """
    🔄 ExcelHandler 후보
    M열 값을 정수로 변환
    """
    for row in range(2, ws.max_row + 1):
        try:
            cell = ws[f"M{row}"]
            cell.value = int(float(cell.value or 0))
        except (ValueError, TypeError):
            cell.value = 0


def highlight_multiple_items(ws: Worksheet) -> None:
    """
    🔄 ExcelHandler 후보
    F열에서 다중 수량 항목 파란색 배경으로 강조
    """
    for row in range(2, ws.max_row + 1):
        f_cell = ws[f"F{row}"]
        clean_text = DataCleanerUtils.clean_product_text(f_cell.value)
        f_cell.value = clean_text
        
        # '개' 문자가 2회 이상 등장하면 파란색 배경
        if clean_text.count("개") >= 2:
            f_cell.fill = BLUE_FILL


def zigzag_merge_packaging(input_path: str) -> str:
    """지그재그 주문 합포장 자동화 처리"""
    # Excel 파일 로드
    ex = ExcelHandler.from_file(input_path)
    ws = ex.ws

    # 1. 기본 서식 적용
    ex.set_basic_format()
    
    # 2. M열 정수 변환
    convert_m_column_to_int(ws)
    
    # 3. M열 → V열 VLOOKUP 처리
    if "Sheet1" in ex.wb.sheetnames:
        lookup_map = DataCleanerUtils.build_lookup_map(ex.wb["Sheet1"])
        for row in range(2, ws.max_row + 1):
            m_val = str(ws[f"M{row}"].value)
            ws[f"V{row}"].value = lookup_map.get(m_val, "")
    
    # 4. D열 수식 설정 (=U+V)
    ex.autofill_d_column(formula="=U{row}+V{row}")
    
    # 5. 상품정보 처리 (다중수량 강조)
    highlight_multiple_items(ws)
    
    # 6. A열 순번 설정
    ex.set_row_number(ws)
    
    # 7. 열 정렬
    ex.set_column_alignment()
    
    # 8. 배경·테두리 제거
    ex.clear_fills_from_second_row()
    ex.clear_borders()
    
    # 9. C→B 정렬
    ex.sort_by_columns([3, 2])  # C열=3, B열=2
    
    # 저장
    base_name = Path(input_path).stem  # 확장자 제거한 파일명
    output_path = ex.happojang_save_file(base_name=base_name)
    
    print(f"◼︎ [{MALL_NAME}] 합포장 자동화 완료!")
    
    return output_path


if __name__ == "__main__":
    test_xlsx = "/Users/smith/Documents/github/OKMart/sabangnet_API/files/test-[기본양식]-합포장용.xlsx"
    zigzag_merge_packaging(test_xlsx)
    print("모든 처리가 완료되었습니다!")