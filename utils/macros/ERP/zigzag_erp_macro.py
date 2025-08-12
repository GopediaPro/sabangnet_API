from utils.excels.excel_handler import ExcelHandler
from utils.excels.excel_column_handler import ExcelColumnHandler
from utils.macros.ERP.utils import average_duplicate_order_address_amounts


class ERPZigzagMacro:
    def __init__(self, file_path: str, is_star: bool = False):
        self.file_path = file_path
        self.is_star = is_star
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

        # sheet1 vlookup 딕셔너리 생성 후 삭제
        vlookup_dict = self.ex.create_vlookup_dict(self.wb)

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
                # VLOOKUP 적용
                self._vlookup_column(ws[f"M{row}"], ws[f"V{row}"], vlookup_dict)
            print(f"[{ws.title}] 서식 및 디자인 적용 완료")

        # 장바구니번호와 수취인주소 조합으로 그룹화 후 평균 금액 적용 (스타배송 모드에서만)
        if self.is_star:
            average_duplicate_order_address_amounts(self.ws)

        output_path = self.ex.save_file(self.file_path)
        print(f"✓ 지그재그 자동화 완료! 최종 파일: {output_path}")
        return output_path

    def _vlookup_column(self, key_cell, value_cell, vlookup_dict):
        """
        VLOOKUP 적용
        args:
            key_cell: 키 셀
            value_cell: 값 셀
            vlookup_dict: VLOOKUP 딕셔너리
        """
        if vlookup_dict.get(str(key_cell.value)):
            value_cell.value = vlookup_dict.get(str(key_cell.value))