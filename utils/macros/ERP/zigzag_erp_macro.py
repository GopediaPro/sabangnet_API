from utils.excels.excel_handler import ExcelHandler
from utils.excels.excel_column_handler import ExcelColumnHandler


class ERPZigzagMacro:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.ex = ExcelHandler.from_file(file_path)
        self.ws = self.ex.ws
        self.wb = self.ex.wb

    def zigzag_erp_macro_run(self) -> str:
        col_h = ExcelColumnHandler()

        # 시트 설정
        sheets_name = ["OK", "IY"]
        site_to_sheet = {
            "오케이마트": "OK",
            "아이예스": "IY",
        }

        # 정렬 기준: 2번째 컬럼(B) → 3번째 컬럼(C) 순으로 정렬
        sort_columns = [2, 3, 5]
        print("시트별 정렬, 시트 분리 시작...")
        headers, data = self.ex.preprocess_and_update_ws(self.ws, sort_columns)
        self.ex.split_and_write_ws_by_site(
            wb=self.wb,
            headers=headers,
            data=data,
            sheets_name=sheets_name,
            site_to_sheet=site_to_sheet,
            site_col_idx=2,
        )
        print("시트별 정렬, 시트 분리 완료")

        print("시트별 서식, 디자인 적용 시작...")
        for ws in self.wb.worksheets:
            self.ex.set_header_style(ws)
            if ws.max_row <= 1:
                continue
            for row in range(2, ws.max_row + 1):
                if ws.title != "자동화":
                    col_h.a_value_column(ws[f"A{row}"])
                else:
                    col_h.a_formula_column(ws[f"A{row}"])
                col_h.d_column(ws[f"D{row}"], ws[f"U{row}"],
                               ws[f"V{row}"])  # =U2+V2
                col_h.e_column(ws[f"E{row}"])
                col_h.f_column(ws[f"F{row}"])
                col_h.convert_int_column(ws[f"M{row}"])
            print(f"[{ws.title}] 서식 및 디자인 적용 완료")

        output_path = self.ex.save_file(self.file_path)
        print(f"✓ 지그재그 자동화 완료! 최종 파일: {output_path}")
        return output_path

    def _vlookup_column(self):
        """
        VLOOKUP 수식 입력 (V열)
        """
        last_row = self.ws.max_row
        for row in range(2, last_row + 1):
            self.ws[f'V{row}'].value = f'=VLOOKUP(M{row},Sheet1!$A:$B,2,0)'
        print("VLOOKUP 수식 입력 완료")
