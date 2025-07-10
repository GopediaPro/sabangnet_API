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
OUTPUT_DIR_NAME = "완료"
MALL_NAME = "기타사이트"
RED_FONT = Font(color="FF0000", bold=True)
BLUE_FILL = PatternFill(start_color="CCFFFF", end_color="CCFFFF", fill_type="solid")

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
    def clean_order_text(txt: str) -> str:
        """주문번호 문자열 정리"""
        if not txt:
            return ""
        txt = txt.replace(" 1개", "").strip()
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
    """기타사이트 주문 합포장 자동화 처리"""
    # Excel 파일 로드
    ex = ExcelHandler.from_file(input_path)
    ws = ex.ws

    # 1. 기본 서식 적용
    ex.set_basic_format()
    
    # 2. C→B 정렬
    ex.sort_by_columns([3, 2])  # C열=3, B열=2
    
    # 3. D열 수식 설정 (=U+V)
    ex.autofill_d_column(formula="=U{row}+V{row}")
    
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
    ex.set_row_number()
    
    # 10. 열 정렬
    ex.set_column_alignment()
    
    # 11. 배경·테두리 제거
    ex.clear_fills_from_second_row()
    ex.clear_borders()
    
    # 12. 숫자형 변환
    ex.convert_numeric_strings(cols=("E", "M", "P", "W"))
    
    # 저장
    output_dir = Path(input_path).parent / OUTPUT_DIR_NAME
    output_dir.mkdir(exist_ok=True)
    output_path = str(output_dir / Path(input_path).name)
    
    ex.wb.save(output_path)
    print(f"◼︎ [{MALL_NAME}] 합포장 자동화 완료!")
    
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
                if "[3000원 환불처리]" not in str(f_cell.value):
                    f_cell.value = f"{f_cell.value} [3000원 환불처리]"
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

if __name__ == "__main__":
    excel_file_path = "/Users/smith/Documents/github/OKMart/sabangnet_API/files/test-[기본양식]-합포장용.xlsx"
    processed_file = etc_site_merge_packaging(excel_file_path)
    print("모든 처리가 완료되었습니다!")