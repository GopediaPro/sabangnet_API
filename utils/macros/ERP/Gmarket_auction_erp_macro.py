import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border
from openpyxl.utils import get_column_letter
import re
from collections import defaultdict
from utils.excel_handler import ExcelHandler


class GmarketAuctionERP:
    def __init__(self, file_path):
        self.ex = ExcelHandler.from_file(file_path)
        self.file_path = file_path
        self.ws = self.ex.ws
        self.wb = self.ex.wb
        self.last_row = self.ws.max_row
        self.last_column = self.ws.max_column
        self.right_alignment = Alignment(horizontal='right')
        self.center_alignment = Alignment(horizontal='center')
        self.light_blue_fill = PatternFill(start_color="ADD8E6", end_color="ADD8E6", fill_type="solid")
        self.dark_green_fill = PatternFill(start_color="008000", end_color="008000", fill_type="solid")
        self.white_font = Font(name='맑은 고딕', size=9, color="FFFFFF", bold=True)
        self.headers = []
        self.df = None

    def step_1_to_12(self):
        """ 
        [1~12단계] 자동화 실행
        """
        print("1~12단계 자동화 시작...")
        self._step_1()
        self._step_2()
        self._step_3()
        self._step_4()
        self._step_5()
        self._step_6()
        self._step_7()
        self._step_8()
        output_path = self.ex.save_file(self.file_path)
        self._step_9_1()
        self._step_9_2()
        self._step_10_1()
        self._step_10_2()
        self._step_10_3()
        self._step_11()
        self._step_12()
        output_path = self.ex.save_file(output_path)
        return output_path

    def _step_1(self):
        """ 
        [1단계] 폰트 및 행 너비 설정
        """
        self.ex.set_basic_format(header_rgb="008000")
    
        print("1단계: 폰트 및 행 높이 설정 완료")
    
    def _step_2(self):
        """ 
        [2단계] D열 수식 활성화 및 채우기
        """
        d2_formula = self.ws['D2'].value
        self.ex.autofill_d_column(start_row=2, end_row=self.last_row, formula=d2_formula)    
    
        print("2단계: D열 수식 처리 완료")
    

    def _step_3(self):
        """ 
        [3단계] 장바구니 중복 제거
        """

        basket_dict = {}
    
        # 첫 번째 패스: 바구니 번호별로 배송비가 있는 첫 번째 행 기록
        for row in range(2, self.last_row + 1):
            basket_no = str(self.ws[f'Q{row}'].value).strip() if self.ws[f'Q{row}'].value else ""
            shipping_cost = self.ws[f'V{row}'].value
            
            if basket_no and basket_no != "":
                if basket_no not in basket_dict:
                    # 배송비가 0이 아니고 비어있지 않은 경우만 기록
                    if shipping_cost and shipping_cost != 0:
                        basket_dict[basket_no] = row
        
        # 두 번째 패스: 중복 바구니의 배송비를 0으로 설정
        for row in range(2, self.last_row + 1):
            basket_no = str(self.ws[f'Q{row}'].value).strip() if self.ws[f'Q{row}'].value else ""
            
            if basket_no and basket_no != "":
                if basket_no in basket_dict:
                    # 첫 번째 발생 행이 아닌 경우 배송비를 0으로 설정
                    if basket_dict[basket_no] != row:
                        self.ws[f'V{row}'].value = 0
        
        print(f"3단계: {len(basket_dict)}개 바구니 중복 제거 완료")
    
    def _step_4(self):
        """ 
        [4단계] A열 순번 수식 + 색칠음영 제거
        """
        # A열에 순번 입력
        self.ex.set_row_number(self.ws, start_row=2, end_row=self.last_row)
        
        # 색칠 음영 제거 (A2:Z까지)
        self.ex.clear_fills_from_second_row()
        
        print("4단계: A열 순번 입력 및 배경색 제거 완료")
        
    def _step_5(self):
        """ 
        [5단계] E열 숫자 변환 및 오른쪽 정렬
        """
        self.ex.set_column_alignment()
        
        # E열 숫자 변환 및 오른쪽 정렬
        # M, W열 숫자 변환
        for row in range(2, self.last_row + 1):
            q_value = self.ws[f'Q{row}'].value
            p_value = self.ws[f'P{row}'].value
            m_value = self.ws[f'M{row}'].value
            w_value = self.ws[f'W{row}'].value
            e_value = self.ws[f'E{row}'].value
            if q_value:
                self.ws[f'Q{row}'].value = self.ex.convert_to_number(q_value)
            if p_value:
                self.ws[f'P{row}'].value = self.ex.convert_to_number(p_value)
            if m_value:
                self.ws[f'M{row}'].value = self.ex.convert_to_number(m_value)
            if w_value:
                self.ws[f'W{row}'].value = self.ex.convert_to_number(w_value)
            if e_value and str(e_value).replace('.', '').replace('-', '').isdigit():
                self.ws[f'E{row}'].value = self.ex.convert_to_number(e_value)
            self.ws[f'E{row}'].alignment = self.right_alignment

    def _step_6(self):
        """ 
        [6단계] F열 ' 1개' 제거
        """
        for row in range(2, self.last_row + 1):
            self.ws[f'F{row}'].value = self.ex.clean_model_name(self.ws[f'F{row}'].value)     
    
        print("6단계: F열 ' 1개' 제거 완료")


    def _step_7(self):
        """ 
        [7단계] F열 모르겠는 셀 색칠음영 (하늘색)
        """
        self.ex.highlight_column(col='F', light_color=self.light_blue_fill, start_row=2, last_row=self.last_row)
        print("7단계: F열 조건부 하이라이트 완료")


    def _step_8(self):
        """ 
        [8단계] 1행 가운데 정렬 + 진한 초록색 배경
        """
        headers = [self.ws.cell(row=1, column=col).value for col in range(1, self.ws.max_column + 1)]

        self.ex.set_header_style(self.ws, headers, self.dark_green_fill, self.white_font, self.center_alignment)
        print("8단계: 헤더 서식 완료")

    def _step_9_1(self):
        """ 
        [9단계] 전체 테두리 제거
        """
        self.ex.clear_borders()
        print("9단계: 테두리 제거 완료")

    def _step_9_2(self):
        """ 
        [9-2단계] 데이터를 DataFrame으로 변환
        """
        
        # 데이터를 DataFrame으로 변환
        data = []
        self.headers = []
        
        # 헤더 읽기
        for col in range(1, self.last_column  + 1):
            header = self.ws.cell(row=1, column=col).value
            self.headers.append(header if header else f"Col{col}")
        
        # 데이터 읽기
        for row in range(2, self.last_row + 1):
            row_data = []
            for col in range(1, self.last_column + 1):
                cell_value = self.ws.cell(row=row, column=col).value
                row_data.append(cell_value)
            data.append(row_data)
        
        # DataFrame 생성 및 정렬
        self.df = pd.DataFrame(data, columns=self.headers)

        # C열(인덱스 2), B열(인덱스 1) 순서로 정렬
        if len(self.df.columns) > 2:
            self.df = self.ex.sort_dataframe_by_c_b(self.df)  
        
        print("9-2, 9-3단계: C열, B열 순서 정렬 완료")

    def _step_10_1(self):
        """ 
        [10-1단계] 시트 분리 준비
        """
         # 기존 시트 삭제
        sheets_to_delete = ["OK,CL,BB", "IY"]
        for sheet_name in sheets_to_delete:
            if sheet_name in self.wb.sheetnames:
                del self.wb[sheet_name]
        
        # 새 시트 생성
        ws_ok = self.wb.create_sheet(title="OK,CL,BB")
        ws_iy = self.wb.create_sheet(title="IY")
        
        # 헤더 복사
        dark_green_fill = PatternFill(start_color="008000", end_color="008000", fill_type="solid")
        white_font = Font(name='맑은 고딕', size=9, color="FFFFFF", bold=True)
        center_alignment = Alignment(horizontal='center')
        

        self.ex.set_header_style(ws_ok, self.headers, dark_green_fill, white_font, center_alignment)
        self.ex.set_header_style(ws_iy, self.headers, dark_green_fill, white_font, center_alignment)
        
        # 열 너비 복사
        for col in range(1, len(self.headers) + 1):
            col_letter = get_column_letter(col)
            src_width = self.ws.column_dimensions[col_letter].width
            ws_ok.column_dimensions[col_letter].width = src_width
            ws_iy.column_dimensions[col_letter].width = src_width
        
        # 행 높이 설정
        ws_ok.row_dimensions[1].height = 15
        ws_iy.row_dimensions[1].height = 15
        
        print("10-1단계: 시트 분리 준비 완료")
            
    def _step_10_2(self):
        """ 
        [10-2단계] 데이터 분류 및 복사
        """
        ok_row = 2
        iy_row = 2
        font = Font(name='맑은 고딕', size=9)
        
        # 정렬된 데이터를 원본 시트에 다시 입력하고 동시에 분리
        for row in range(2, self.last_row + 1):
            for col in range(1, len(self.headers) + 1):
                self.ws.cell(row=row, column=col).value = None
        
        for idx, row_data in self.df.iterrows():
            excel_row = idx + 2
            
            # 원본 시트에 데이터 입력
            for col_idx, value in enumerate(row_data, 1):
                self.ws.cell(row=excel_row, column=col_idx, value=value)
            
            # B열(사이트 정보)에서 계정명 추출
            site_value = str(row_data.iloc[1]) if pd.notna(row_data.iloc[1]) else ""
            account_name = ""
            
            if "]" in site_value and site_value.startswith("["):
                try:
                    account_name = site_value[1:site_value.index("]")]
                except:
                    account_name = ""
            
            # 계정명에 따라 시트 분리
            if account_name in ["오케이마트", "클로버즈", "베이지베이글"]:
                # OK,CL,BB 시트에 복사
                for col_idx, value in enumerate(row_data, 1):
                    cell = self.ws.cell(row=ok_row, column=col_idx, value=value)
                    cell.font = font
                self.ws.row_dimensions[ok_row].height = 15
                ok_row += 1
                
            elif account_name == "아이예스":
                # IY 시트에 복사
                for col_idx, value in enumerate(row_data, 1):
                    cell = self.ws.cell(row=iy_row, column=col_idx, value=value)
                    cell.font = font
                self.ws.row_dimensions[iy_row].height = 15
                iy_row += 1
        
        print(f"10-2단계: 데이터 분리 완료 (OK: {ok_row-2}행, IY: {iy_row-2}행)")
        
    def _step_10_3(self):
        """ 
        [10-3단계] A열 수식 값 변환
        """
        for ws in self.wb.worksheets:
            if ws.max_row > 1:
                self.ex.set_row_number(ws)
        
        print("10-3단계: A열 순번 재설정 완료")
        
    def _step_11(self):
        """ 
        [11단계] L열 처리
        """
        red_font = Font(color="FF0000")
    
        for ws in self.wb.worksheets:
            if ws.max_row <= 1:
                continue
            
            for row in range(2, self.last_row + 1):
                l_value = ws[f'L{row}'].value
                if l_value:
                    l_value_str = str(l_value).strip()
                    if l_value_str == "신용":
                        ws[f'L{row}'].value = ""
                    elif l_value_str == "착불":
                        ws[f'L{row}'].font = red_font
    
        print("11단계: L열 처리 완료 (신용→공백, 착불→빨간색)")

    def _step_12(self):
        """ 
        [12단계] 모든 시트에 서식 재적용
        """
        for ws in self.wb.worksheets:
            if self.last_row <= 1:
                continue
            
            # 기본 폰트 적용
            self.ex.set_basic_format(header_rgb="008000")
            
            # A, B, D, E, G열 정렬
            self.ex.set_column_alignment()
            
            # ================================
            # [12단계] F열 조건부 서식 재적용
            # ================================
            
            # F열 조건부 서식 재적용
            for row in range(2, self.last_row + 1):
                if self.last_row >= 6:
                    f_value = self.ws[f'F{row}'].value
                    cell_value = str(f_value).strip() if f_value else ""
                    
                    should_highlight = False
                    
                    if cell_value == "" or cell_value == "None":
                        should_highlight = True
                    elif cell_value and all(c == '#' for c in cell_value):
                        should_highlight = True
                    elif cell_value.endswith("개") and cell_value[:-1].isdigit():
                        should_highlight = True
                    
                    if should_highlight:
                        ws[f'F{row}'].fill = self.light_blue_fill

            print("12단계: 서식 재적용 완료")
        
    

def gok_erp_automation_full(file_path):
    """
    G,옥 ERP 자동화 전체 프로세스 실행
    
    Args:
        file_path (str): 처리할 Excel 파일 경로
    """
    
    print("G,옥 ERP 자동화 전체 프로세스 시작...")
    
    # 1~12단계 실행
    class_instance = GmarketAuctionERP(file_path)
    final_file = class_instance.step_1_to_12()
    
    print(f"✓ G,옥 ERP 자동화 완료! 최종 파일: {final_file}")
    return final_file


# 사용 예시
if __name__ == "__main__":
    # 파일 경로를 지정하세요
    excel_file_path = "your_gok_file.xlsx"
    
    try:
        # G,옥 ERP 자동화 전체 프로세스 실행
        class_instance = GmarketAuctionERP(excel_file_path)
        final_file = class_instance.step_1_to_12()
        
        print("G,옥 ERP 자동화가 성공적으로 완료되었습니다!")
        
    except Exception as e:
        print(f"오류가 발생했습니다: {e}")
        import traceback
        traceback.print_exc()