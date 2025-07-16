from utils.excel_handler import ExcelHandler
from utils.excel_column_handler import ExcelColumnHandler
from collections import defaultdict
from openpyxl.styles import PatternFill, Font, Alignment, Border
import re


class GmarketAuctionMacro:
    def __init__(self, file_path):
        self.ex = ExcelHandler.from_file(file_path)
        self.file_path = file_path
        self.ws = self.ex.ws
        self.wb = self.ex.wb
        self.basket_set = set()
        self.headers = None

    def gauc_erp_macro_run(self):
        macro = ExcelColumnHandler()
        self.basket_set = set()

        # 장바구니 중복 제거 & 금액 컬럼 계산 먼저 실행
        for row in range(2, self.ws.max_row + 1):
            self._basket_duplicate_column(
                self.ws[f"Q{row}"], self.ws[f"V{row}"])
            macro.d_column(
                self.ws[f"D{row}"], self.ws[f"O{row}"], self.ws[f"P{row}"], self.ws[f"V{row}"])

        # 정렬
        sheets_name = ["자동화", "OK,CL,BB", "IY"]
        site_to_sheet = {
            "오케이마트": "OK,CL,BB",
            "클로버프": "OK,CL,BB",
            "베이지베이글": "OK,CL,BB",
            "아이예스": "IY",
        }

        # 정렬 기준: 2번째 컬럼(B) → 3번째 컬럼(C) 순으로 정렬
        sort_columns = [2, 3]
        print("시트별 정렬, 시트 분리 시작...")
        self.ex.split_and_write_ws_by_site(
            ws=self.ws,
            wb=self.wb,
            site_col_idx=2,
            sheets_name=sheets_name,
            site_to_sheet=site_to_sheet,
            sort_columns=sort_columns
        )
        print("시트별 정렬, 시트 분리 완료")
        
        print("시트별 서식, 디자인 적용 시작...")
        for ws in self.wb.worksheets:
            if ws.max_row <= 1:
                continue
            for row in range(2, ws.max_row + 1):
                if ws.title != "자동화":
                    macro.a_value_column(ws[f"A{row}"])
                else:
                    macro.a_formula_column(ws[f"A{row}"])
                macro.d_column(
                    ws[f"D{row}"], ws[f"O{row}"], ws[f"P{row}"], ws[f"V{row}"])
                macro.f_column(ws[f"F{row}"])
                macro.l_column(ws[f"L{row}"])
                macro.e_column(ws[f"E{row}"])
                macro.convert_int_column(ws[f"O{row}"])
                macro.convert_int_column(ws[f"P{row}"])
                macro.convert_int_column(ws[f"V{row}"])
                macro.convert_int_column(ws[f"M{row}"])
                macro.convert_int_column(ws[f"Q{row}"])
                macro.convert_int_column(ws[f"W{row}"])
                macro.convert_int_column(ws[f"R{row}"])
                macro.convert_int_column(ws[f"S{row}"])
                self.ex.set_header_style(ws)
                print(f"[{ws.title}] 서식 및 디자인 적용 완료")


        output_path = self.ex.save_file(self.file_path)
        print(f"✓ G,옥 ERP 자동화 완료! 최종 파일: {output_path}")
        return output_path

    def _basket_duplicate_column(self, basket_cell, shipping_cell):
        basket_no = str(basket_cell.value).strip() if basket_cell.value else ""

        if not basket_no:
            return

        if basket_no in self.basket_set:
            # 이미 등장한 바구니 번호면 배송비 0으로
            shipping_cell.value = 0
        else:
            # 첫 등장 - 세트에 추가
            self.basket_set.add(basket_no)
