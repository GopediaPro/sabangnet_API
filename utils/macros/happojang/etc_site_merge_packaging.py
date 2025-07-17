"""기타사이트 합포장 자동화 모듈"""

from __future__ import annotations
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set

from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet
from utils.excel_handler import ExcelHandler

import pandas as pd

# 설정 상수
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
class ETCSiteConfig:
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

class ETCOrderUtils:
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

def process_order_numbers(ws: Worksheet) -> None:
    """
    🔄 ExcelHandler 후보
    사이트별 주문번호 처리
    """
    for row in range(2, ws.max_row + 1):
        site = str(ws[f"B{row}"].value or "")
        order_raw = str(ws[f"E{row}"].value or "")
        
        # 사이트별 주문번호 길이 제한 적용
        for site_name, length in ETCSiteConfig.ORDER_NUMBER_LENGTHS.items():
            if site_name in site:
                ws[f"E{row}"].value = order_raw[:length]
                break
                
        # 쿠팡 특수 처리
        if "쿠팡" in site and "/" in order_raw:
            slash_count = order_raw.count("/")
            pure_length = len(order_raw.replace("/", ""))
            each_len = pure_length // (slash_count + 1)
            ws[f"E{row}"].value = order_raw[:each_len]


def etc_site_merge_packaging(input_path: str) -> str:
    """기타사이트 주문 합포장 자동화 처리 (VBA 매크로 14단계 시트분리 포함)"""
    # Excel 파일 로드
    ex = ExcelHandler.from_file(input_path)
    ws = ex.ws
    
    # ========== VBA 매크로 14단계: 시트분리 (OK, IY, BB) ==========
    # 원본 시트에서 시트분리 수행
    splitter = ETCSheetManager(ws, ACCOUNT_MAPPING)
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
    base_name = Path(input_path).stem  # 확장자 제거한 파일명
    output_path = ex.happojang_save_file(base_name=base_name)
    ex.wb.close()
    print(f"◼︎ [{MALL_NAME}] 합포장 자동화 완료!")
    print(f"  - 시트분리 완료: {', '.join(REQUIRED_SHEETS)}")
    
    return output_path


class ETCDeliveryFeeHandler:
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
            
            # V열 값이 "/" 구분자 형태인 경우 첫 번째 값 사용
            v_value = v_cell.value
            if v_value and "/" in str(v_value):
                v_val = float(str(v_value).split("/")[0].strip() or 0)
            else:
                v_val = float(v_value or 0)
            
            # U열 값도 동일하게 처리
            u_value = self.ws[f"U{row}"].value
            if u_value and "/" in str(u_value):
                u_val = float(str(u_value).split("/")[0].strip() or 0)
            else:
                u_val = float(u_value or 0)

            # 배송비 분할 대상
            if any(s in site for s in ETCSiteConfig.DELIVERY_SPLIT_SITES) and "/" in order_text:
                count = len(order_text.split("/"))
                if v_val > 3000 and count > 0:
                    v_cell.value = round(v_val / count)
                    v_cell.font = RED_FONT

            # 무료배송
            elif any(s in site for s in ETCSiteConfig.FREE_DELIVERY_SITES):
                v_cell.value = 0
                v_cell.font = RED_FONT

            # 토스 (3만원 이상 무료)
            elif "토스" in site:
                v_cell.value = 0 if u_val > 30000 else 3000
                v_cell.font = RED_FONT


class ETCSpecialCaseHandler:
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


class ETCSheetManager:
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
            account = ETCOrderUtils.extract_bracket_text(self.ws[f"B{r}"].value)
            
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
        
        print(f"📋 기타사이트 자동화 로직 시작 (시트: {ws.title}, 총 {ws.max_row}행)")
        
        # 1. 기본 서식 적용
        ex.set_basic_format()

        # 2. P, V열 "/" 구분자 합산 처리 및 D열 계산을 위한 임시 처리
        print("🔄 2단계: P, V열 '/' 구분자 처리")
        
        # P열과 V열의 원본 값을 임시 저장
        p_original_values = {}
        v_original_values = {}
        
        for row in range(2, ws.max_row + 1):
            p_original_values[row] = ws[f'P{row}'].value
            v_original_values[row] = ws[f'V{row}'].value
        
        # P열 "/" 구분자 합산 처리 (D열 계산용)
        ex.sum_prow_with_slash()
        # V열 "/" 구분자 첫 번째 값 처리 (D열 계산용)
        self.process_v_column_slash_values(ws)
        
        # 3. C→B 정렬
        ex.sort_by_columns([2, 3])
        
        # 4. D열 수식 설정 (처리된 P, V 값으로 계산)
        ex.calculate_d_column_values(first_col='O', second_col='P', third_col='V')
        
        # 5. P열과 V열을 원본 "/" 구분자 형태로 복원
        print("🔄 5단계: P, V열 원본 형태 복원")
        for row in range(2, ws.max_row + 1):
            if row in p_original_values:
                ws[f'P{row}'].value = p_original_values[row]
            if row in v_original_values:
                ws[f'V{row}'].value = v_original_values[row]
        
        # 6. 사이트별 배송비 처리
        ETCDeliveryFeeHandler(ws).process_delivery_fee()
        
        # 7. 주문번호 처리
        process_order_numbers(ws)
        
        # 8. 전화번호 처리
        print("🔄 8단계: 전화번호 처리")
        for row in range(2, ws.max_row + 1):
            for col in ('H', 'I'):
                cell_value = ws[f'{col}{row}'].value
                ws[f'{col}{row}'].value = ex.format_phone_number(cell_value)
        
        # 9. 특수 케이스 처리
        print("🔄 9단계: 특수 케이스 처리")
        special = ETCSpecialCaseHandler(ws)
        special.process_kakao_jeju()
        special.process_l_column()
        
        # 10. F열 텍스트 정리
        print("🔄 10단계: F열 텍스트 정리")
        for row in range(2, ws.max_row + 1):
            ws[f"F{row}"].value = ETCOrderUtils.clean_order_text(ws[f"F{row}"].value)
        
        # 10.5. F열 "+" 구분자 기준 행 분할 (클로버프 계정만, VBA 18단계 이후 실행)
        print("🔄 10.5단계: F열 '+' 구분자 기준 행 분할 (클로버프 계정만)")
        self.split_rows_by_plus_separator(ws)
        
        # 11. A열 순번 설정
        print("🔄 11단계: A열 순번 설정")
        ex.set_row_number(ws)

        # 12. 문자열→숫자 변환 
        print("🔄 12단계: 문자열→숫자 변환")
        ex.convert_numeric_strings(cols=("F","M", "P", "Q", "W", "AA"))

        # 13. 열 정렬
        print("🔄 13단계: 열 정렬")
        ex.set_column_alignment()
        # F열 왼쪽정렬 
        for row in range(1, ws.max_row + 1):
            ws[f"F{row}"].alignment = Alignment(horizontal='left')

        # 14. 배경·테두리 제거
        print("🔄 14단계: 배경·테두리 제거")
        ex.set_basic_format()
        ex.clear_fills_from_second_row()
        ex.clear_borders()
        
        print(f"✅ 기타사이트 자동화 로직 완료 (최종 {ws.max_row}행)")

    def process_v_column_slash_values(self, ws: Worksheet) -> None:
        """
        V열의 "/" 구분자로 나뉜 경우 첫 번째 숫자만 추출
        예: "3000/3000" → 3000
        """
        for row in range(2, ws.max_row + 1):
            cell_val = ws[f'V{row}'].value
            if cell_val and "/" in str(cell_val):
                parts = str(cell_val).split("/")
                if parts:
                    first_part = parts[0].strip()
                    if first_part and first_part.replace('.', '').replace('-', '').isdigit():
                        try:
                            ws[f'V{row}'].value = float(first_part)
                        except ValueError:
                            pass  # 변환 실패 시 원래 값 유지

    def split_rows_by_plus_separator(self, ws: Worksheet) -> None:
        """
        B열에 "클로버프"가 포함된 행에서 F열의 "+" 또는 "/" 구분자를 기준으로 행을 분할
        예: B열="[클로버프]옥션2.0", F열="상품A + 상품B" → 두 개의 별도 행으로 분할
        관련 열들도 함께 분할 처리 (E열 주문번호, 기타 슬래시 구분자 열들)
        """
        print(f"F열 구분자 기준 행 분할 시작 (총 {ws.max_row}행, 클로버프 대상만)")
        split_count = 0
        
        # 먼저 분할 대상 행 확인 (B열에 "클로버프" 포함 + F열에 구분자 있는 경우만)
        split_targets = []
        for row in range(2, ws.max_row + 1):
            b_value = ws[f'B{row}'].value
            f_value = ws[f'F{row}'].value
            
            # B열에 "클로버프"가 포함된 경우만 처리
            if b_value and "클로버프" in str(b_value):
                if f_value:
                    f_str = str(f_value)
                    if " + " in f_str or ("/" in f_str and not f_str.startswith("http")):
                        split_targets.append((row, f_str))
        
        print(f"분할 대상 행: {len(split_targets)}개 (B열 '클로버프' 포함 행만)")
        for row, value in split_targets:
            print(f"  행 {row}: '{value}'")
        
        # 역순으로 처리 (행 삽입 시 인덱스 변화 방지)
        for row in range(ws.max_row, 1, -1):
            b_value = ws[f'B{row}'].value
            f_value = ws[f'F{row}'].value
            
            # B열에 "클로버프"가 포함된 경우만 처리
            if not (b_value and "클로버프" in str(b_value)):
                continue
                
            if f_value:
                f_str = str(f_value)
                # " + " 또는 "/" 구분자 확인
                if " + " in f_str:
                    separator = " + "
                elif "/" in f_str and not f_str.startswith("http"):  # URL이 아닌 경우만
                    separator = "/"
                else:
                    continue
                    
                print(f"  행 {row}: '{f_value}' → '{separator}' 기준 분할 시작 (B열: '{b_value}')")
                split_count += 1
                
                # 구분자 기준으로 분할
                products = f_str.split(separator)
                if len(products) > 1:
                    # 관련 열들의 "/" 구분자 값들도 함께 분할 준비
                    e_values = self._split_slash_values(ws[f'E{row}'].value, len(products))  # 주문번호
                    l_values = self._split_slash_values(ws[f'L{row}'].value, len(products))  # 결제방식
                    m_values = self._split_slash_values(ws[f'M{row}'].value, len(products))  # 송장번호
                    n_values = self._split_slash_values(ws[f'N{row}'].value, len(products))  # 배송메모
                    o_values = self._split_slash_values(ws[f'O{row}'].value, len(products))  # 판매가
                    p_values = self._split_slash_values(ws[f'P{row}'].value, len(products))  # 수수료
                    s_values = self._split_slash_values(ws[f'S{row}'].value, len(products))  # S열
                    u_values = self._split_slash_values(ws[f'U{row}'].value, len(products))  # 구매가
                    v_values = self._split_slash_values(ws[f'V{row}'].value, len(products))  # 배송비
                    x_values = self._split_slash_values(ws[f'X{row}'].value, len(products))  # X열
                    y_values = self._split_slash_values(ws[f'Y{row}'].value, len(products))  # 상품번호
                    z_values = self._split_slash_values(ws[f'Z{row}'].value, len(products))  # 상품명상세
                    aa_values = self._split_slash_values(ws[f'AA{row}'].value, len(products))  # 옵션정보
                    ab_values = self._split_slash_values(ws[f'AB{row}'].value, len(products))  # 기타
                    
                    print(f"    분할 개수: {len(products)}개 상품")
                    print(f"    주문번호 분할: {e_values}")
                    
                    # O열, P열, U열 원본 값 저장 (분할 시 균등 분할용)
                    original_o_value = ws[f'O{row}'].value
                    original_p_value = ws[f'P{row}'].value
                    original_u_value = ws[f'U{row}'].value
                    
                    # 분할 개수 계산
                    product_count = len(products)
                    print(f"    상품 분할 개수: {product_count}개")
                    
                    # 먼저 원본 행을 첫 번째 상품으로 수정
                    first_product = products[0].strip()
                    ws[f'F{row}'].value = first_product
                    ws[f'E{row}'].value = e_values[0] if e_values else ""
                    ws[f'G{row}'].value = 1
                    ws[f'H{row}'].value = "010-0000-0000"
                    ws[f'I{row}'].value = "010-0000-0000"
                    ws[f'L{row}'].value = ""  # 분할된 행은 결제방식 빈값
                    ws[f'M{row}'].value = m_values[0] if m_values else ""
                    ws[f'N{row}'].value = n_values[0] if n_values else ""
                    
                    # O열은 원본 값을 분할 개수로 나누어 설정
                    if original_o_value and isinstance(original_o_value, (int, float)):
                        ws[f'O{row}'].value = original_o_value / product_count
                    
                    # P열은 분할된 값 사용
                    if p_values and p_values[0]:
                        try:
                            ws[f'P{row}'].value = float(p_values[0])
                        except (ValueError, TypeError):
                            ws[f'P{row}'].value = p_values[0]
                    
                    # S열은 분할된 값 사용
                    ws[f'S{row}'].value = s_values[0] if s_values else ""
                    
                    # U열은 원본 값을 분할 개수로 나누어 설정
                    if original_u_value and isinstance(original_u_value, (int, float)):
                        ws[f'U{row}'].value = original_u_value / product_count
                    
                    # V열은 분할된 값 사용
                    if v_values and v_values[0]:
                        try:
                            ws[f'V{row}'].value = float(v_values[0])
                        except (ValueError, TypeError):
                            ws[f'V{row}'].value = v_values[0]
                    
                    # X열은 분할된 값 사용
                    ws[f'X{row}'].value = x_values[0] if x_values else ""
                    
                    # Y열은 분할된 값 사용
                    ws[f'Y{row}'].value = y_values[0] if y_values else ""
                    
                    # Z열은 분할된 값 사용
                    ws[f'Z{row}'].value = z_values[0] if z_values else ""
                    
                    # AA열은 분할된 값 사용
                    ws[f'AA{row}'].value = aa_values[0] if aa_values else ""
                    
                    # AB열에 각 상품 정보 설정
                    ws[f'AB{row}'].value = f"{first_product} 1개"
                    
                    # D열 계산 (첫 번째 상품) - 수정된 값으로 계산
                    o_val = ws[f'O{row}'].value or 0
                    p_val = ws[f'P{row}'].value or 0
                    v_val = ws[f'V{row}'].value or 0
                    try:
                        calculated_d = float(o_val) + float(p_val) + float(v_val)
                        ws[f'D{row}'].value = calculated_d
                        print(f"    첫 번째 상품 D열 계산: {o_val} + {p_val} + {v_val} = {calculated_d}")
                    except (ValueError, TypeError) as e:
                        print(f"    첫 번째 상품 D열 계산 오류: {e}")
                        ws[f'D{row}'].value = ""
                    
                    # 나머지 상품들을 새 행으로 추가 (두 번째 상품부터)
                    # 원본 행 바로 아래부터 연속으로 삽입
                    for i in range(1, len(products)):
                        product = products[i]
                        new_row = row + 1  # 원본 행 바로 아래에 삽입
                        print(f"    새 행 {new_row} 삽입: '{product.strip()}' (원본 행 {row} 바로 아래)")
                        
                        # 새 행 삽입 (원본 행 바로 아래)
                        ws.insert_rows(new_row)
                        
                        # 기존 행의 기본 데이터를 새 행에 복사
                        for col in range(1, ws.max_column + 1):
                            col_letter = ws.cell(row=1, column=col).column_letter
                            if col_letter not in ['D', 'E', 'F', 'G', 'H', 'I', 'L', 'M', 'N', 'O', 'P', 'S', 'U', 'V', 'X', 'Y', 'Z', 'AA', 'AB']:
                                ws.cell(row=new_row, column=col).value = ws.cell(row=row, column=col).value
                        
                        # D열은 분할된 행에서 계산된 값으로 설정
                        o_val = original_o_value / product_count if original_o_value and isinstance(original_o_value, (int, float)) else 0
                        p_val = p_values[i] if i < len(p_values) and p_values[i] else 0
                        v_val = v_values[i] if i < len(v_values) and v_values[i] else 0
                        try:
                            p_val = float(p_val) if p_val else 0
                            v_val = float(v_val) if v_val else 0
                            calculated_d = o_val + p_val + v_val
                            ws[f'D{new_row}'].value = calculated_d
                            print(f"    새 행 {new_row} D열 계산: {o_val} + {p_val} + {v_val} = {calculated_d}")
                        except (ValueError, TypeError) as e:
                            print(f"    새 행 {new_row} D열 계산 오류: {e}")
                            ws[f'D{new_row}'].value = ""
                        
                        # 분할된 특수 열들 입력
                        ws[f'F{new_row}'].value = product.strip()
                        ws[f'E{new_row}'].value = e_values[i] if i < len(e_values) else ""
                        ws[f'G{new_row}'].value = 1  # 수량 1로 설정
                        ws[f'H{new_row}'].value = "010-0000-0000"  # 분할된 행은 기본 전화번호
                        ws[f'I{new_row}'].value = "010-0000-0000"  # 분할된 행은 기본 전화번호
                        ws[f'L{new_row}'].value = ""  # 분할된 행은 결제방식 빈값
                        ws[f'M{new_row}'].value = m_values[i] if i < len(m_values) else ""
                        ws[f'N{new_row}'].value = n_values[i] if i < len(n_values) else ""
                        
                        # O열은 원본 값을 분할 개수로 나누어 설정
                        if original_o_value and isinstance(original_o_value, (int, float)):
                            ws[f'O{new_row}'].value = original_o_value / product_count
                        elif i < len(o_values) and o_values[i]:
                            try:
                                ws[f'O{new_row}'].value = float(o_values[i]) / product_count
                            except (ValueError, TypeError):
                                ws[f'O{new_row}'].value = o_values[i]
                        else:
                            ws[f'O{new_row}'].value = ""
                        
                        # P열은 분할된 값 사용
                        if i < len(p_values) and p_values[i]:
                            try:
                                ws[f'P{new_row}'].value = float(p_values[i])
                            except (ValueError, TypeError):
                                ws[f'P{new_row}'].value = p_values[i]
                        else:
                            ws[f'P{new_row}'].value = ""
                        
                        # S열은 분할된 값 사용
                        ws[f'S{new_row}'].value = s_values[i] if i < len(s_values) else ""
                        
                        # U열은 원본 값을 분할 개수로 나누어 설정
                        if original_u_value and isinstance(original_u_value, (int, float)):
                            ws[f'U{new_row}'].value = original_u_value / product_count
                        elif i < len(u_values) and u_values[i]:
                            try:
                                ws[f'U{new_row}'].value = float(u_values[i]) / product_count
                            except (ValueError, TypeError):
                                ws[f'U{new_row}'].value = u_values[i]
                        else:
                            ws[f'U{new_row}'].value = ""
                        
                        # V열은 분할된 값 사용
                        if i < len(v_values) and v_values[i]:
                            try:
                                ws[f'V{new_row}'].value = float(v_values[i])
                            except (ValueError, TypeError):
                                ws[f'V{new_row}'].value = v_values[i]
                        else:
                            ws[f'V{new_row}'].value = ""
                        
                        # X열은 분할된 값 사용
                        ws[f'X{new_row}'].value = x_values[i] if i < len(x_values) else ""
                        
                        # Y열은 분할된 값 사용
                        ws[f'Y{new_row}'].value = y_values[i] if i < len(y_values) else ""
                        
                        # Z열은 분할된 값 사용
                        ws[f'Z{new_row}'].value = z_values[i] if i < len(z_values) else ""
                        
                        # AA열은 분할된 값 사용
                        ws[f'AA{new_row}'].value = aa_values[i] if i < len(aa_values) else ""
                        
                        # AB열에 각 상품 정보 설정
                        ws[f'AB{new_row}'].value = f"{product.strip()} 1개"
                    
                    print(f"    분할 완료: 총 {len(products)}개 상품으로 분할됨")
        
        print(f"F열 구분자 분할 완료: {split_count}개 행 분할됨")
        print(f"분할 후 총 행 수: {ws.max_row}행")

    def _split_slash_values(self, value, expected_count: int) -> List[str]:
        """
        "/" 구분자로 나뉜 값들을 리스트로 분할
        expected_count만큼 값이 없으면 빈 문자열로 채움
        """
        if not value:
            return [""] * expected_count
        
        val_str = str(value).strip()
        if "/" in val_str:
            parts = val_str.split("/")
        else:
            # "/" 구분자가 없으면 첫 번째 값만 사용하고 나머지는 빈 문자열
            parts = [val_str]
        
        # 필요한 개수만큼 값이 없으면 빈 문자열로 채움
        while len(parts) < expected_count:
            parts.append("")
        
        result = [part.strip() for part in parts[:expected_count]]
        return result

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