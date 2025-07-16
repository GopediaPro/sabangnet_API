from utils.excels.excel_handler import ExcelHandler
from utils.excels.excel_column_handler import ExcelColumnHandler


class ERPBrandiMacro:
    def __init__(self, file_path):
        self.ex = ExcelHandler.from_file(file_path)
        self.file_path = file_path
        self.ws = self.ex.ws

    def brandi_erp_macro_run(self):
        ws = self.ws
        col_h = ExcelColumnHandler()

        # 정렬 기준: 3번째 컬럼(C) 순으로 정렬
        sort_columns = [3]  # 정렬 확인 필요

        self.ex.set_header_style(ws)
        print('헤더 스타일 적용 완료')
        self.ex.preprocess_and_update_ws(ws, sort_columns)
        print('정렬 및 데이터 업데이트 완료')

        print('서식 적용 시작...')
        for row in range(2, ws.max_row + 1):
            col_h.d_column(ws[f"D{row}"], ws[f"O{row}"],
                           ws[f"P{row}"], ws[f"V{row}"])
            col_h.f_column(ws[f"F{row}"])
            col_h.h_i_column(ws[f"H{row}"])
            col_h.h_i_column(ws[f"I{row}"])
            col_h.a_formula_column(ws[f"A{row}"])
            self._jeju_address_column(ws, row, ws[f"J{row}"])  # 확인필요
            col_h.e_column(ws[f"E{row}"])
            col_h.convert_int_column(ws[f"P{row}"])
            col_h.convert_int_column(ws[f"P{row}"])
            col_h.convert_int_column(ws[f"W{row}"])
        print(f'[{ws.title}] 서식 적용 완료')

        output_path = self.ex.save_file(self.file_path)
        print(f"브랜디 ERP 자동화 완료!\n처리된 파일: {output_path}")
        return output_path

    def _jeju_address_column(self, ws, row, cell):
        """
        제주 주소 포맷
        args:
            cell: 대상 셀 (J)
        """
        if cell.value and "제주" in str(cell.value):
            self.ex.process_jeju_address(
                ws, row, f_col='F', j_col='J')
