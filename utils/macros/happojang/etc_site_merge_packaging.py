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
        - 분할된 행에 대한 재처리 포함
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
                v_val = float(v_value or 0) if v_value else 0
            
            # U열 값도 동일하게 처리
            u_value = self.ws[f"U{row}"].value
            if u_value and "/" in str(u_value):
                u_val = float(str(u_value).split("/")[0].strip() or 0)
            else:
                u_val = float(u_value or 0) if u_value else 0

            # 분할된 행에서 V열이 비어있는 경우 배송비 로직 재적용
            if v_value is None or v_value == "":
                
                # 배송비 분할 대상
                if any(s in site for s in ETCSiteConfig.DELIVERY_SPLIT_SITES) and "/" in order_text:
                    count = len(order_text.split("/"))
                    # 기본 배송비 3000원 적용 후 분할
                    if count > 0:
                        v_cell.value = round(3000 / count)
                        v_cell.font = RED_FONT

                # 무료배송
                elif any(s in site for s in ETCSiteConfig.FREE_DELIVERY_SITES):
                    v_cell.value = 0
                    v_cell.font = RED_FONT

                # 토스 (3만원 이상 무료)
                elif "토스" in site:
                    v_cell.value = 0 if u_val > 30000 else 3000
                    v_cell.font = RED_FONT
                    
            else:
                # V열에 값이 있는 경우 기존 로직 적용
                
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
        
        # 1. 기본 서식 적용
        ex.set_basic_format()
        
        # 2. C→B 정렬
        ex.sort_by_columns([2, 3])
        
        # 3. D열 수식 설정 (사용자 요구사항에 맞는 P, V 처리)
        self._calculate_d_column_custom(ws)
        
        # 4. 사이트별 배송비 처리
        ETCDeliveryFeeHandler(ws).process_delivery_fee()
        
        # 5. 주문번호 처리
        process_order_numbers(ws)
        
        # 6. 전화번호 처리
        for row in range(2, ws.max_row + 1):
            for col in ('H', 'I'):
                cell_value = ws[f'{col}{row}'].value
                ws[f'{col}{row}'].value = ex.format_phone_number(cell_value)
        
        # 7. 특수 케이스 처리
        special = ETCSpecialCaseHandler(ws)
        special.process_kakao_jeju()
        special.process_l_column()
        
        # 7.5. F열 "+" 구분자 기준 행 분할 (클로버프 계정만, F열 텍스트 정리 전에 실행)
        self.split_rows_by_plus_separator(ws)
        
        # 8. F열 텍스트 정리
        for row in range(2, ws.max_row + 1):
            ws[f"F{row}"].value = ETCOrderUtils.clean_order_text(ws[f"F{row}"].value)

        # 9. 문자열→숫자 변환 
        ex.convert_numeric_strings(cols=("F","M", "P", "Q", "W", "AA"))

        # 10. 열 정렬
        ex.set_column_alignment()
        # F열 왼쪽정렬 
        for row in range(1, ws.max_row + 1):
            ws[f"F{row}"].alignment = Alignment(horizontal='left')

        # 11. 배경·테두리 제거, A열 순번 설정
        ex.set_row_number(ws)
        ex.clear_fills_from_second_row()
        ex.clear_borders()

    def _calculate_d_column_custom(self, ws: Worksheet) -> None:
        """
        D열 계산: O + P(슬래시 합산) + V(슬래시 합산)
        - P열: "780/780" → 780 + 780 = 1560
        - V열: "3000/3000" → 3000 + 3000 = 6000
        """
        for row in range(2, ws.max_row + 1):
            o_val = ws[f'O{row}'].value or 0
            p_val = ws[f'P{row}'].value or 0
            v_val = ws[f'V{row}'].value or 0
            
            # O열 처리 (숫자로 변환)
            try:
                o_num = float(o_val) if o_val else 0
            except (ValueError, TypeError):
                o_num = 0
            
            # P열 처리: "/" 구분자가 있으면 모든 숫자를 합산
            p_num = 0
            if p_val and "/" in str(p_val):
                p_parts = str(p_val).split("/")
                for part in p_parts:
                    try:
                        p_num += float(part.strip())
                    except (ValueError, TypeError):
                        pass  # 숫자가 아닌 경우 무시
            else:
                try:
                    p_num = float(p_val) if p_val else 0
                except (ValueError, TypeError):
                    p_num = 0
            
            # V열 처리: "/" 구분자가 있으면 모든 숫자를 합산 (P열과 동일)
            v_num = 0
            if v_val and "/" in str(v_val):
                v_parts = str(v_val).split("/")
                for part in v_parts:
                    try:
                        v_num += float(part.strip())
                    except (ValueError, TypeError):
                        pass  # 숫자가 아닌 경우 무시
            else:
                try:
                    v_num = float(v_val) if v_val else 0
                except (ValueError, TypeError):
                    v_num = 0
            
            # D열에 계산 결과 설정
            calculated_d = o_num + p_num + v_num
            ws[f'D{row}'].value = calculated_d

    def split_rows_by_plus_separator(self, ws: Worksheet) -> None:
        """
        B열에 "클로버프"가 포함된 행에서 G열(수량) 기준으로 행을 분할 (VBA 로직과 동일)
        - G = 1: 원본 행 복사하여 새 행 1개 추가
        - G = 2: "/" 구분자 기준으로 2개 행으로 분할
        """
        split_count = 0
        
        # 먼저 분할 대상 행 확인 (B열에 "클로버프" 포함 + G열 수량이 1 또는 2)
        split_targets = []
        for row in range(2, ws.max_row + 1):
            b_value = ws[f'B{row}'].value
            g_value = ws[f'G{row}'].value
            
            # B열에 "클로버프"가 포함되고 G열이 1 또는 2인 경우만 처리
            if b_value and "클로버프" in str(b_value):
                if g_value in [1, 2]:
                    split_targets.append((row, g_value))
        
        # 역순으로 처리 (행 삽입 시 인덱스 변화 방지)
        for row in range(ws.max_row, 1, -1):
            b_value = ws[f'B{row}'].value
            g_value = ws[f'G{row}'].value
            
            # B열에 "클로버프"가 포함되고 G열이 1 또는 2인 경우만 처리
            if not (b_value and "클로버프" in str(b_value) and g_value in [1, 2]):
                continue
                
            split_count += 1
            
            if g_value == 1:
                # 수량 1: 원본 행 복사하여 새 행 1개 추가
                self._create_single_copy_row(ws, row)
                
            elif g_value == 2:
                # 수량 2: "/" 구분자 기준으로 2개 행으로 분할
                self._create_split_rows(ws, row)

    def _create_single_copy_row(self, ws: Worksheet, original_row: int) -> None:
        """수량 1인 경우: 원본 행을 그대로 복사하여 새 행 1개 추가"""
        new_row = original_row + 1
        
        # 새 행 삽입
        ws.insert_rows(new_row)
        
        # 원본 행의 모든 데이터를 새 행에 복사 (A, D, G 제외)
        for col in range(1, ws.max_column + 1):
            col_letter = ws.cell(row=1, column=col).column_letter
            if col_letter not in ['A', 'D', 'G']:
                ws.cell(row=new_row, column=col).value = ws.cell(row=original_row, column=col).value
        
        # 새 행 전용 설정
        ws[f'G{new_row}'].value = 1  # 수량 1
        ws[f'H{new_row}'].value = "010-0000-0000"  # 기본 전화번호
        ws[f'I{new_row}'].value = "010-0000-0000"  # 기본 전화번호
        
        # D열 계산 (O + P + V, slash 처리 후 첫 값 사용)
        self._calculate_d_column(ws, new_row)

    def _create_split_rows(self, ws: Worksheet, original_row: int) -> None:
        """수량 2인 경우: VBA와 100% 동일한 방식으로 분할"""
        
        # 분할 대상 열들의 원본 값 가져오기
        split_columns = ['E', 'F', 'L', 'M', 'N', 'O', 'P', 'S', 'T', 'U', 'V', 'X', 'Y', 'Z', 'AA']
        original_values = {}
        split_data = {}
        
        for col in split_columns:
            original_values[col] = ws[f'{col}{original_row}'].value
            split_data[col] = self._split_slash_values(original_values[col], 2)
        
        # 원본 O열, U열 값 저장 (균등 분할용)
        original_o_value = ws[f'O{original_row}'].value
        original_u_value = ws[f'U{original_row}'].value
        
        # 2개의 새 행 생성
        for i in range(2):
            new_row = original_row + 1 + i
            
            # 새 행 삽입
            ws.insert_rows(new_row)
            
            # 원본 행의 기본 데이터 복사 (분할되지 않는 열들)
            for col in range(1, ws.max_column + 1):
                col_letter = ws.cell(row=1, column=col).column_letter
                if col_letter not in ['A', 'D', 'E', 'F', 'G', 'H', 'I', 'L', 'M', 'N', 'O', 'P', 'S', 'T', 'U', 'V', 'X', 'Y', 'Z', 'AA', 'AB']:
                    ws.cell(row=new_row, column=col).value = ws.cell(row=original_row, column=col).value
            
            # 분할된 열들 설정
            for col in split_columns:
                if col == 'L':
                    # L열은 "/" 구분자가 있어도 항상 빈칸으로 처리
                    ws[f'{col}{new_row}'].value = ""
                elif col == 'T':
                    # T열은 "/" 구분자가 있어도 항상 빈칸으로 처리
                    ws[f'{col}{new_row}'].value = ""
                elif col == 'O':
                    # O열은 균등 분할
                    if original_o_value and isinstance(original_o_value, (int, float)):
                        ws[f'{col}{new_row}'].value = original_o_value / 2
                    else:
                        ws[f'{col}{new_row}'].value = split_data[col][i] if i < len(split_data[col]) else ""
                elif col == 'U':
                    # U열은 균등 분할
                    if original_u_value and isinstance(original_u_value, (int, float)):
                        ws[f'{col}{new_row}'].value = original_u_value / 2
                    else:
                        ws[f'{col}{new_row}'].value = split_data[col][i] if i < len(split_data[col]) else ""
                elif col == 'V':
                    # V열은 VBA 특별 처리: "/" 구분자가 있으면 분할된 각 값 사용
                    original_v_value = original_values['V']
                    if original_v_value and "/" in str(original_v_value):
                        # "/" 구분자가 있는 경우 분할된 값 사용
                        value = split_data[col][i] if i < len(split_data[col]) and split_data[col][i] else ""
                        if value and str(value).replace('.', '').replace('-', '').isdigit():
                            try:
                                ws[f'{col}{new_row}'].value = float(value)
                            except (ValueError, TypeError):
                                ws[f'{col}{new_row}'].value = value
                        else:
                            ws[f'{col}{new_row}'].value = value
                    else:
                        # "/" 구분자가 없는 경우 원본 값 유지
                        ws[f'{col}{new_row}'].value = original_v_value
                elif col == 'Z':
                    # Z열은 특별한 패턴으로 분할: "상품명:사이즈/가격/개수" 단위로 분할
                    original_z_value = original_values['Z']
                    if original_z_value:
                        z_split_parts = self._split_z_column_value(str(original_z_value), 2)
                        ws[f'{col}{new_row}'].value = z_split_parts[i] if i < len(z_split_parts) else ""
                    else:
                        ws[f'{col}{new_row}'].value = ""
                else:
                    # 기타 열들은 분할된 값 사용
                    value = split_data[col][i] if i < len(split_data[col]) and split_data[col][i] else ""
                    ws[f'{col}{new_row}'].value = value
            
            # 새 행 전용 설정
            ws[f'G{new_row}'].value = 1  # 수량 1
            ws[f'H{new_row}'].value = "010-0000-0000"  # 기본 전화번호
            ws[f'I{new_row}'].value = "010-0000-0000"  # 기본 전화번호
            
            # AB열에 상품 정보 설정
            f_value = split_data['F'][i] if i < len(split_data['F']) and split_data['F'][i] else ""
            ws[f'AB{new_row}'].value = f"{f_value.strip()} 1개" if f_value else "1개"
            
            # D열 계산
            self._calculate_d_column(ws, new_row)
        
        # 원본 행의 V열 원본 값 유지 (VBA 로직과 동일)
        original_v_value = original_values['V']
        if original_v_value and "/" in str(original_v_value):
            ws[f'V{original_row}'].value = original_v_value

    def _calculate_d_column(self, ws: Worksheet, row: int) -> None:
        """D열 계산: O + P + V (slash 처리 후 첫 값 사용)"""
        o_val = ws[f'O{row}'].value or 0
        p_val = ws[f'P{row}'].value or 0
        v_val = ws[f'V{row}'].value or 0
        
        # P열이 "/" 구분자 포함 시 첫 번째 값만 사용
        if p_val and "/" in str(p_val):
            p_val = float(str(p_val).split("/")[0].strip() or 0)
        else:
            p_val = float(p_val) if p_val else 0
        
        # V열이 "/" 구분자 포함 시 첫 번째 값만 사용
        if v_val and "/" in str(v_val):
            v_val = float(str(v_val).split("/")[0].strip() or 0)
        else:
            v_val = float(v_val) if v_val else 0
        
        try:
            calculated_d = float(o_val) + p_val + v_val
            ws[f'D{row}'].value = calculated_d
        except (ValueError, TypeError):
            ws[f'D{row}'].value = ""

    def _split_z_column_value(self, value: str, expected_count: int) -> List[str]:
        """
        Z열 특별 분할 로직: "상품명:사이즈/가격/개수" 패턴으로 분할
        예: "WMSLV7_블랙:2XL/0원/1개/WMSLV7_화이트:2XL/0원/1개" 
        → ["WMSLV7_블랙:2XL/0원/1개", "WMSLV7_화이트:2XL/0원/1개"]
        """
        if not value:
            return [""] * expected_count
        
        # "상품명:사이즈/가격/개수" 패턴을 찾기 위한 정규식
        # 패턴: 문자/숫자/기호 + : + 문자/숫자 + / + 숫자원 + / + 숫자개
        import re
        
        # 더 간단한 접근: /숫자개/ 패턴을 찾아서 그 다음 항목까지를 하나의 단위로 인식
        # 예: "1개/WMSLV7_화이트" 패턴에서 "1개" 다음부터 새로운 항목 시작
        
        parts = []
        current_part = ""
        segments = value.split("/")
        
        i = 0
        while i < len(segments):
            current_part += segments[i]
            
            # "숫자개" 패턴을 찾으면 하나의 완성된 항목으로 간주
            if re.search(r'\d+개$', segments[i]):
                parts.append(current_part.strip())
                current_part = ""
            elif i < len(segments) - 1:
                current_part += "/"
            
            i += 1
        
        # 마지막 부분이 남아있으면 추가
        if current_part.strip():
            parts.append(current_part.strip())
        
        # expected_count만큼 맞추기
        while len(parts) < expected_count:
            parts.append("")
        
        result = parts[:expected_count]
        
        return result

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
            # 파트가 expected_count보다 적으면 빈 문자열로 채움
            while len(parts) < expected_count:
                parts.append("")
            result = [part.strip() for part in parts[:expected_count]]
        else:
            # "/" 구분자가 없으면 첫 번째 값만 사용하고 나머지는 빈 문자열
            result = [val_str] + [""] * (expected_count - 1)
        
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