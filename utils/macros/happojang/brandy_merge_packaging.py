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
OUTPUT_DIR_NAME = "완료"
MALL_NAME = "브랜디"
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


class ProductUtils:
    """상품 정보 처리 유틸리티"""
    
    @staticmethod
    def clean_product_text(txt: str | None) -> str:
        """
        🔄 ExcelHandler 후보
        상품명 문자열 정리 (' 1개' 제거)
        """
        return str(txt or "").replace(" 1개", "").strip()


class PhoneUtils:
    """전화번호 처리 유틸리티"""
    
    @staticmethod
    def format_phone(val: str | None) -> str:
        """전화번호 포맷팅 (01012345678 → 010-1234-5678)"""
        if not val:
            return ""
        digits = re.sub(r"\D", "", str(val))
        if len(digits) == 11:
            return f"{digits[:3]}-{digits[3:7]}-{digits[7:]}"
        return str(val)


class GroupMerger:
    """주문 데이터 그룹핑 및 병합 처리"""
    
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
            total = 0.0
            for row in rows:
                cell_val = self.ws[f"D{row}"].value
                if isinstance(cell_val, str) and cell_val.startswith("="):
                    # 수식이 있는 경우 O+P+V 각각 계산
                    o_val = float(self.ws[f"O{row}"].value or 0)
                    p_val = float(self.ws[f"P{row}"].value or 0)
                    v_val = float(self.ws[f"V{row}"].value or 0)
                    total += (o_val + p_val + v_val)
                else:
                    total += float(cell_val or 0)
            self.ws[f"D{base_row}"].value = total
            
            # F열 모델명 결합
            models = []
            for row in rows:
                model = self.ws[f"F{row}"].value
                if model:
                    clean_model = ProductUtils.clean_product_text(model)
                    if clean_model:
                        models.append(clean_model)
            self.ws[f"F{base_row}"].value = " + ".join(models)
            
            # 나머지 행은 삭제 대상으로 표시
            rows_to_delete.extend(rows[1:])
            
        return sorted(rows_to_delete, reverse=True)  # 역순 정렬(삭제용)


def process_phones(ws: Worksheet) -> None:
    """전화번호 처리 (H/I열)"""
    for row in range(2, ws.max_row + 1):
        for col in ("H", "I"):
            phone = PhoneUtils.format_phone(ws[f"{col}{row}"].value)
            if phone != str(ws[f"{col}{row}"].value):
                ws[f"{col}{row}"].value = phone


def process_jeju_orders(ex: ExcelHandler) -> None:
    """제주도 주문 처리"""
    ws = ex.ws
    for row in range(2, ws.max_row + 1):
        if "제주" in str(ws[f"J{row}"].value or ""):
            ws[f"J{row}"].font = RED_FONT
            if "[3000원 환불처리]" not in str(ws[f"F{row}"].value):
                ws[f"F{row}"].value = f"{ws[f'F{row}'].value} [3000원 환불처리]"
            ws[f"F{row}"].fill = BLUE_FILL


def brandy_merge_packaging(input_path: str) -> str:
    """브랜디 주문 합포장 자동화 처리"""
    # Excel 파일 로드
    ex = ExcelHandler.from_file(input_path)
    ws = ex.ws

    # 1. 기본 서식 적용
    ex.set_basic_format()

    # 2. C→B 정렬
    ex.sort_by_columns([3, 2])  # C열=3, B열=2
    
    # 3. 그룹핑 및 병합
    merger = GroupMerger(ws)
    merger.group_by_product_and_receiver()
    rows_to_delete = merger.merge_rows()
    
    # 중복 행 삭제 (역순으로)
    for row_idx in rows_to_delete:
        ws.delete_rows(row_idx)
    
    # 4. D열 수식 재설정
    ex.autofill_d_column(formula="=O{row}+P{row}+V{row}")
    
    # 5. A열 순번 재설정
    ex.set_row_number()
    
    # 6. 전화번호 처리
    process_phones(ws)
    
    # 7. 제주도 주문 처리
    process_jeju_orders(ex)
    
    # 8. 열 정렬
    ex.set_column_alignment()
    
    # 9. 배경·테두리 제거
    ex.clear_fills_from_second_row()
    ex.clear_borders()
    
    # 저장
    output_dir = Path(input_path).parent / OUTPUT_DIR_NAME
    output_dir.mkdir(exist_ok=True)
    output_path = str(output_dir / Path(input_path).name)
    
    ex.wb.save(output_path)
    print(f"◼︎ [{MALL_NAME}] 합포장 자동화 완료!")
    
    return output_path


if __name__ == "__main__":
    test_path = "/Users/smith/Documents/github/OKMart/sabangnet_API/files/test-[기본양식]-합포장용.xlsx"
    brandy_merge_packaging(test_path)