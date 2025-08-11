from utils.excels.excel_handler import ExcelHandler
from utils.excels.excel_column_handler import ExcelColumnHandler
from utils.macros.ERP.utils import average_duplicate_order_address_amounts


class ERPBrandiMacro:
    def __init__(self, file_path, is_star: bool = False):
        self.ex = ExcelHandler.from_file(file_path)
        self.file_path = file_path
        self.is_star = is_star
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
            col_h.d_column(ws[f"D{row}"],
                           ws[f"P{row}"], ws[f"V{row}"]) # =P2+V2
            col_h.f_column(ws[f"F{row}"])
            col_h.h_i_column(ws[f"H{row}"])
            col_h.h_i_column(ws[f"I{row}"])
            col_h.a_formula_column(ws[f"A{row}"])
            col_h.e_column(ws[f"E{row}"])
            col_h.convert_int_column(ws[f"P{row}"])
        print(f'[{ws.title}] 서식 적용 완료')

        # 장바구니번호와 수취인주소 조합으로 그룹화 후 평균 금액 적용 (스타배송 모드에서만)
        if self.is_star:
            average_duplicate_order_address_amounts(self.ws)

        output_path = self.ex.save_file(self.file_path)
        print(f"브랜디 ERP 자동화 완료!\n처리된 파일: {output_path}")
        return output_path
