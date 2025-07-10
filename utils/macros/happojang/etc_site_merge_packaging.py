"""기타사이트 합포장 자동화 모듈"""

from __future__ import annotations
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set

from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet
from utils.excel_handler import ExcelHandler

import pandas as pd

# 설정 상수
OUTPUT_PREFIX = "기타사이트_합포장_자동화_"
MALL_NAME = "기타사이트"
RED_FONT = Font(color="FF0000", bold=True)
BLUE_FILL = PatternFill(start_color="CCFFFF", end_color="CCFFFF", fill_type="solid")

# 시트 분리 설정 
ACCOUNT_MAPPING = {
    "OK": ["오케이마트"],
    "IY": ["아이예스"], 
    "BB": ["베이지베이글"]
}

# 필수 생성 시트 목록
REQUIRED_SHEETS = list(ACCOUNT_MAPPING.keys())

# 사이트 설정
class SiteConfig:
    # 배송비 분할 대상
    DELIVERY_SPLIT_SITES: Set[str] = {
        "롯데온", "보리보리", "스마트스토어", "톡스토어"
    }
    
    # 배송비 무료 사이트
    FREE_DELIVERY_SITES: Set[str] = {"오늘의집"}
    
    # 주문번호 길이 제한
    ORDER_NUMBER_LENGTHS: Dict[str, int] = {
        "YES24": 11,
        "CJ온스타일": 26,
        "GSSHOP": 21,
        "스마트스토어": 16,
        "에이블리": 13,
        "올웨이즈": 14,
        "위메프": 13,
        "인터파크": 12,
        "쿠팡": 13,
        "티몬": 12,
        "하이마트": 12
    }
    
    # 숫자 변환 대상 사이트
    NUMERIC_SITES: Set[str] = {
        "에이블리", "오늘의집", "쿠팡", "텐바이텐", "NS홈쇼핑", 
        "그립", "보리보리", "카카오선물하기", "톡스토어", "토스"
    }


class PhoneUtils:
    """전화번호 처리 유틸리티"""
    
    @staticmethod
    def format_phone(val: str | None) -> str:
        """전화번호 포맷팅 (01012345678 → 010-1234-5678)"""
        if not val:
            return ""
        digits = re.sub(r"\D", "", str(val))
        if len(digits) == 11 and digits.startswith("010"):
            return f"{digits[:3]}-{digits[3:7]}-{digits[7:]}"
        return str(val)


class OrderUtils:
    """주문번호 처리 유틸리티"""
    
    @staticmethod
    def clean_order_text(txt) -> str:
        """주문번호 문자열 정리 (안전한 타입 변환 포함)"""
        if not txt:
            return ""
        # 안전한 문자열 변환 (float, int, str 모두 처리)
        txt = str(txt).replace(" 1개", "").strip()
        txt = txt.replace("/", " + ")
        return txt

    @staticmethod
    def extract_bracket_text(text: str | None) -> str:
        """[계정명] 형식에서 계정명만 추출"""
        if not text:
            return ""
        match = re.search(r"\[(.*?)\]", str(text))
        return match.group(1) if match else ""

def to_num(val) -> float:
    """'12,345원' → 12345.0 (실패 시 0)."""
    try:
        return float(re.sub(r"[^\d.-]", "", str(val))) if str(val).strip() else 0.0
    except ValueError:
        return 0.0

def process_order_numbers(ws: Worksheet) -> None:
    """
    🔄 ExcelHandler 후보
    사이트별 주문번호 처리
    """
    for row in range(2, ws.max_row + 1):
        site = str(ws[f"B{row}"].value or "")
        order_raw = str(ws[f"E{row}"].value or "")
        
        # 사이트별 주문번호 길이 제한 적용
        for site_name, length in SiteConfig.ORDER_NUMBER_LENGTHS.items():
            if site_name in site:
                ws[f"E{row}"].value = order_raw[:length]
                break
                
        # 쿠팡 특수 처리
        if "쿠팡" in site and "/" in order_raw:
            slash_count = order_raw.count("/")
            pure_length = len(order_raw.replace("/", ""))
            each_len = pure_length // (slash_count + 1)
            ws[f"E{row}"].value = order_raw[:each_len]


def process_phones(ws: Worksheet) -> None:
    """전화번호 처리 (H/I열)"""
    for row in range(2, ws.max_row + 1):
        for col in ("H", "I"):
            phone = PhoneUtils.format_phone(ws[f"{col}{row}"].value)
            if phone != str(ws[f"{col}{row}"].value):
                ws[f"{col}{row}"].value = phone


def etc_site_merge_packaging(input_path: str) -> str:
    """기타사이트 주문 합포장 자동화 처리 (VBA 매크로 14단계 시트분리 포함)"""
    # Excel 파일 로드
    ex = ExcelHandler.from_file(input_path)
    ws = ex.ws
    
    # ========== VBA 매크로 14단계: 시트분리 (OK, IY, BB) ==========
    # 원본 시트에서 시트분리 수행
    splitter = EtcSiteSheetManager(ws, ACCOUNT_MAPPING)
    rows_by_sheet = splitter.get_rows_by_sheet()
    
    # 원본 시트에 자동화 로직 적용
    splitter.apply_automation_logic(ws)
    
    # 모든 필수 시트 생성 (데이터 유무와 무관하게 OK, IY, BB 시트 생성)
    for sheet_name in REQUIRED_SHEETS:
        splitter.copy_to_new_sheet(
            ex.wb,
            sheet_name, 
            rows_by_sheet.get(sheet_name, [])
        )
    
    # 저장
    output_path = str(
        Path(input_path).with_name(OUTPUT_PREFIX + Path(input_path).name)
    )
    ex.wb.save(output_path)
    ex.wb.close()
    print(f"◼︎ [{MALL_NAME}] 합포장 자동화 완료!")
    print(f"  - 시트분리 완료: {', '.join(REQUIRED_SHEETS)}")
    
    return output_path


class DeliveryFeeHandler:
    """사이트별 배송비 처리"""
    
    def __init__(self, ws: Worksheet):
        self.ws = ws
        
    def process_delivery_fee(self) -> None:
        """
        🔄 ExcelHandler 후보
        사이트별 배송비 처리
        - 롯데온/보리보리 등: 주문 수로 나누기
        - 오늘의집: 무료배송
        - 토스: 3만원 이상 무료
        """
        for row in range(2, self.ws.max_row + 1):
            site = str(self.ws[f"B{row}"].value or "")
            order_text = str(self.ws[f"X{row}"].value or "")
            v_cell = self.ws[f"V{row}"]
            v_val = float(v_cell.value or 0)
            u_val = float(self.ws[f"U{row}"].value or 0)

            # 배송비 분할 대상
            if any(s in site for s in SiteConfig.DELIVERY_SPLIT_SITES) and "/" in order_text:
                count = len(order_text.split("/"))
                if v_val > 3000 and count > 0:
                    v_cell.value = round(v_val / count)
                    v_cell.font = RED_FONT

            # 무료배송
            elif any(s in site for s in SiteConfig.FREE_DELIVERY_SITES):
                v_cell.value = 0
                v_cell.font = RED_FONT

            # 토스 (3만원 이상 무료)
            elif "토스" in site:
                v_cell.value = 0 if u_val > 30000 else 3000
                v_cell.font = RED_FONT


class SpecialCaseHandler:
    """특수 케이스 처리"""
    
    def __init__(self, ws: Worksheet):
        self.ws = ws
        
    def process_kakao_jeju(self) -> None:
        """카카오 + 제주도 주문 처리"""
        for row in range(2, self.ws.max_row + 1):
            site = str(self.ws[f"B{row}"].value or "")
            addr = str(self.ws[f"J{row}"].value or "")
            
            if "카카오" in site and "제주" in addr:
                # F열 안내문구 추가 및 배경색
                f_cell = self.ws[f"F{row}"]
                if "[3000원 연락해야함]" not in str(f_cell.value):
                    f_cell.value = f"{f_cell.value} [3000원 연락해야함]"
                f_cell.fill = BLUE_FILL
                
                # J열 빨간색 굵게
                self.ws[f"J{row}"].font = RED_FONT
                
    def process_l_column(self) -> None:
        """L열 신용/착불 처리"""
        for row in range(2, self.ws.max_row + 1):
            val = str(self.ws[f"L{row}"].value or "")
            if val == "신용":
                self.ws[f"L{row}"].value = ""
            elif val == "착불":
                self.ws[f"L{row}"].font = RED_FONT


class EtcSiteSheetManager:
    """기타사이트 시트 분리 및 자동화 로직 적용 (VBA 매크로 14단계 구현)"""
    
    def __init__(self, ws: Worksheet, account_mapping: Dict[str, List[str]]):
        self.ws = ws
        self.account_mapping = account_mapping
        self.last_row = ws.max_row
        self.last_col = ws.max_column
        
        # 열 너비 저장 (VBA 매크로와 동일)
        self.col_widths = [
            ws.column_dimensions[get_column_letter(c)].width
            for c in range(1, self.last_col + 1)
        ]

    def get_rows_by_sheet(self) -> Dict[str, List[int]]:
        """시트별 행 번호 매핑 생성 (VBA ExtractBracketText 로직 구현)"""
        rows_by_sheet = defaultdict(list)
        
        for r in range(2, self.last_row + 1):
            # B열에서 [계정명] 추출 (VBA ExtractBracketText와 동일)
            account = OrderUtils.extract_bracket_text(self.ws[f"B{r}"].value)
            
            # 각 시트의 계정 목록과 정확히 비교
            for sheet_name, accounts in self.account_mapping.items():
                if account in accounts:
                    rows_by_sheet[sheet_name].append(r)
                    break
                    
        return rows_by_sheet

    def create_empty_sheet(self, wb, sheet_name: str) -> Worksheet:
        """빈 시트 생성 (헤더와 열 너비만 복사) - VBA 매크로와 동일"""
        # 기존 시트 삭제 (VBA: On Error Resume Next)
        if sheet_name in wb.sheetnames:
            del wb[sheet_name]
            
        new_ws = wb.create_sheet(sheet_name)
        
        # 제목행 복사 (VBA: sourceSheet.Rows(1).Copy destSheet.Rows(1))
        for c in range(1, self.last_col + 1):
            new_ws.cell(row=1, column=c, 
                       value=self.ws.cell(row=1, column=c).value)
            # 열너비 복사 (VBA: destSheet.Columns(c).ColumnWidth = colWidth(c))
            new_ws.column_dimensions[get_column_letter(c)].width = self.col_widths[c - 1]
            
        return new_ws

    def copy_sheet_data(self, ws: Worksheet, row_indices: List[int]) -> None:
        """시트에 데이터 행 복사 (VBA: sourceSheet.Rows(r).Copy Destination:=destSheet.Rows(targetRow))"""
        if not row_indices:
            return
            
        target_row = 2
        for r in row_indices:
            for c in range(1, self.last_col + 1):
                ws.cell(row=target_row, column=c, 
                       value=self.ws.cell(row=r, column=c).value)
            target_row += 1
        
        # A열 순번 재부여 (VBA: destSheet.Cells(r, "A").Value = r - 1)
        for r in range(2, target_row):
            ws[f"A{r}"].value = r - 1

    def apply_automation_logic(self, ws: Worksheet) -> None:
        """자동화 로직 적용 (VBA 매크로 21단계까지의 모든 로직)"""
        # Excel 핸들러로 기본 처리 적용
        ex = ExcelHandler(ws)
        
        # 1. 기본 서식 적용
        ex.set_basic_format()
        
        # 2. C→B 정렬
        ex.sort_by_columns([3, 2])
        
        # 3. D열 수식 설정
        ex.autofill_d_column(formula="=O{row}+P{row}+V{row}")
        
        # 4. 사이트별 배송비 처리
        DeliveryFeeHandler(ws).process_delivery_fee()
        
        # 5. 주문번호 처리
        process_order_numbers(ws)
        
        # 6. 전화번호 처리
        process_phones(ws)
        
        # 7. 특수 케이스 처리
        special = SpecialCaseHandler(ws)
        special.process_kakao_jeju()
        special.process_l_column()
        
        # 8. F열 텍스트 정리
        for row in range(2, ws.max_row + 1):
            ws[f"F{row}"].value = OrderUtils.clean_order_text(ws[f"F{row}"].value)
        
        # 9. A열 순번 설정
        ex.set_row_number(ws)

        # 10. 문자열→숫자 변환 
        ex.convert_numeric_strings(cols=("F","M", "P", "Q", "W", "AA"))

        # 11. 열 정렬
        ex.set_column_alignment()
        
        # 12. 배경·테두리 제거
        ex.clear_fills_from_second_row()
        ex.clear_borders()

    def copy_to_new_sheet(self, 
                         wb, 
                         sheet_name: str, 
                         row_indices: List[int] = None) -> None:
        """지정된 행들로 새 시트 생성 (데이터가 없어도 빈 시트 생성)"""
        new_ws = self.create_empty_sheet(wb, sheet_name)
        if row_indices:
            self.copy_sheet_data(new_ws, row_indices)
            
        # 모든 시트에 자동화 로직 적용
        self.apply_automation_logic(new_ws)

if __name__ == "__main__":
    excel_file_path = "/Users/smith/Documents/github/OKMart/sabangnet_API/files/test-[기본양식]-합포장용.xlsx"
    processed_file = etc_site_merge_packaging(excel_file_path)
    print("모든 처리가 완료되었습니다!")