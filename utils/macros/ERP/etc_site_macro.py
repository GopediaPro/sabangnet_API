import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
import re
from collections import defaultdict
from utils.excel_handler import ExcelHandler


class ECTSiteMacro:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.ex = ExcelHandler.from_file(file_path)
        self.ws = self.ex.ws
        self.wb = self.ex.wb
        self.last_row = self.ws.max_row
        self.last_col = self.ws.max_column
        self.right_alignment = Alignment(horizontal='right')
        self.center_alignment = Alignment(horizontal='center')
        self.light_blue_fill = PatternFill(
            start_color="ADD8E6", end_color="ADD8E6", fill_type="solid")
        self.green_fill = PatternFill(
            start_color="006100", end_color="006100", fill_type="solid")
        self.headers = [cell.value for cell in self.ws[1]]
        self.df = None

    def step_1_to_13(self) -> str:
        """
        1~13단계 자동화 실행
        """
        print("1~13단계 자동화 시작...")
        self._step_1()  
        self._step_2()  
        self._step_3()  
        self._step_4()  
        self._step_5()  
        self._step_6()  
        self._step_7()
        self._step_8()
        # ws 로직
        for ws in self.wb.worksheets:
            if ws.max_row <= 1:
                continue
            self._step_13(ws)
        output_path = self.ex.save_file(self.file_path)
        return output_path

    def _step_1(self):
        """
        [1단계] 데이터를 DataFrame으로 변환
        """
        # 데이터를 DataFrame으로 변환
        self.df = self.ex.to_dataframe(self.ws)
        self.headers = list(self.df.columns)

        # C열(인덱스 2), B열(인덱스 1) 순서로 정렬
        if len(self.df.columns) > 2:
            self.df = self.ex.sort_dataframe_by_c_b(
                self.df, c_col='수취인명', b_col='사이트')

        print("1단계: C열, B열 순서 정렬 완료")

        
        self.df.iloc[:, 0] = range(1, len(self.df) + 1)  # A열 순번 재설정

    def _step_2(self):
        # 사이트별 처리 (오늘의집, 톡스토어, 롯데온, 보리보리, 스마트스토어)
        order_dict = {}
        for idx, row in self.df.iterrows():
            site_text = str(row.iloc[1])
            if "오늘의집" in site_text:
                self.df.at[idx, self.df.columns[21]] = 0
            elif "톡스토어" in site_text:
                order_key = str(row.iloc[9]).strip()
                if order_key and order_key != "":
                    if order_key in order_dict:
                        self.df.at[idx, self.df.columns[21]] = 0
                    else:
                        order_dict[order_key] = True
            elif any(site in site_text for site in ["롯데온", "보리보리", "스마트스토어"]):
                order_key = str(row.iloc[4]).strip()
                if order_key and order_key != "":
                    if order_key in order_dict:
                        self.df.at[idx, self.df.columns[21]] = 0
                    else:
                        order_dict[order_key] = True
        print("2단계: 사이트별 처리 완료")

    def _step_3(self):
        # 토스 처리 (V열, U열 합산)
        u_sum_dict = defaultdict(float)
        row_list_dict = defaultdict(list)
        for idx, row in self.df.iterrows():
            if "토스" in str(row.iloc[1]):
                order_key = str(row.iloc[4]).strip()
                if order_key and order_key != "":
                    u_value = float(row.iloc[20]) if pd.notna(
                        row.iloc[20]) else 0
                    u_sum_dict[order_key] += u_value
                    row_list_dict[order_key].append(idx)
        for order_key, rows in row_list_dict.items():
            if u_sum_dict[order_key] > 30000:
                for row_idx in rows:
                    self.df.at[row_idx, self.df.columns[21]] = 0
            else:
                for i, row_idx in enumerate(rows):
                    self.df.at[row_idx, self.df.columns[21]
                               ] = 3000 if i == 0 else 0
        print("3단계: 토스 처리 완료")
    
    def _step_4(self):
        # 전화번호 포맷팅 (H, I)
        for col_idx in [7, 8]:
            for idx in self.df.index:
                phone_val = str(self.df.iloc[idx, col_idx]).strip()
                if (len(phone_val) == 11 and phone_val.startswith('010') and phone_val.isdigit()):
                    formatted_phone = f"{phone_val[:3]}-{phone_val[3:7]}-{phone_val[7:]}"
                    self.df.iloc[idx, col_idx] = formatted_phone
        print("4단계: 전화번호 포맷팅 완료")

    def _step_5(self):
        # 사이트별 주문번호 숫자 변환
        site_list = ["에이블리", "오늘의집", "쿠팡", "텐바이텐",
                     "NS홈쇼핑", "그립", "보리보리", "카카오선물하기", "톡스토어", "토스"]
        row_dict = defaultdict(list)
        for idx, row in self.df.iterrows():
            site_text = str(row.iloc[1])
            for site in site_list:
                if site in site_text:
                    row_dict[site].append(idx)
                    break
        for site, indices in row_dict.items():
            for idx in indices:
                order_num = self.df.iloc[idx, 4]
                if pd.notna(order_num) and str(order_num).replace('.', '').isdigit():
                    self.df.iloc[idx, 4] = int(float(order_num))
        print("5단계: 사이트별 주문번호 숫자 변환 완료")


    def _step_6(self):
        # 카카오 + 제주 처리
        for idx in self.df.index:
            if ("카카오" in str(self.df.iloc[idx, 1]) and "제주" in str(self.df.iloc[idx, 9])):
                f_val = str(self.df.iloc[idx, 5])
                if "[3000원 연락해야함]" not in f_val:
                    self.df.iloc[idx, 5] = f_val + " [3000원 연락해야함]"
        print("6단계: 카카오 + 제주 처리 완료")
    
    def _step_7(self):
        """
        [7단계] 워크시트에 정렬된 데이터 덮어쓰기
        """
        for row_idx, row_data in enumerate(self.df.itertuples(index=False), start=2):
            for col_idx, value in enumerate(row_data, start=1):
                self.ws.cell(row=row_idx, column=col_idx, value=value if value or value == 0 else "")
        print("7단계: 워크시트에 정렬된 데이터 덮어쓰기 완료")

    
    def _step_8(self):
        """
        [8단계] 시트 분리
        """
        site_filters = ["오케이마트", "아이예스", "베이지베이글"]
        site_codes = ["OK", "IY", "BB"]
        for i, (site_filter, site_code) in enumerate(zip(site_filters, site_codes)):
            if site_code in self.wb.sheetnames:
                del self.wb[site_code]
            new_ws = self.wb.create_sheet(title=site_code)
            for col_idx, header in enumerate(self.headers, 1):
                new_ws.cell(row=1, column=col_idx, value=header)
                new_ws.cell(row=1, column=col_idx).fill = self.green_fill
            filtered_df = self.df[self.df.iloc[:,
                                               1].str.contains(site_filter, na=False)]
            for row_idx, (_, row) in enumerate(filtered_df.iterrows(), 2):
                for col_idx, value in enumerate(row, 1):
                    new_ws.cell(row=row_idx, column=col_idx, value=value)
            for row_idx in range(2, new_ws.max_row + 1):
                new_ws.cell(row=row_idx, column=1, value=row_idx - 1)
            for col_idx in range(1, len(self.headers) + 1):
                col_letter = openpyxl.utils.get_column_letter(col_idx)
                new_ws.column_dimensions[col_letter].width = self.ws.column_dimensions[col_letter].width
        print("8단계: 시트 분리 완료")

    def _step_9(self, ws):
        """
        [9단계] D열 수식 활성화 및 채우기
        """
        d2_formula = self.ws['D2'].value
        self.ex.autofill_d_column(ws=ws,
            start_row=2, end_row=ws.max_row, formula=d2_formula)
        print("9단계: D열 수식 처리 완료")

    def _step_10(self, ws):
        """
        [10단계] M, P, Q,W 숫자 변환
        """
        cols_names = ['M', 'P', 'Q','W']
        self.ex.convert_numeric_strings(
            ws=ws, start_row=2, end_row=self.last_row, cols=cols_names)
        print("10단계: M, P, Q,W 숫자 변환 완료")
    
    def _step_11(self, ws):
        # L열 처리 (배송비 관련) & V열이 0인 경우 빨간색 굵게
        red_font = Font(color="FF0000")

        for row in range(2, ws.max_row + 1):
            l_value = ws[f'L{row}'].value
            if l_value:
                l_value_str = str(l_value).strip()
                if l_value_str == "신용":
                    ws[f'L{row}'].value = ""
                elif l_value_str == "착불":
                    ws[f'L{row}'].font = red_font
            if ws[f'V{row}'].value == 0:
                ws[f'V{row}'].font = Font(color="FF0000", bold=True)
                ws[f'V{row}'].alignment = Alignment(horizontal='right')
        print("11단계: L열 & V열 처리 완료")

    def _step_12(self, ws):
        # F열 처리 (상품명)
        for row in range(2, ws.max_row + 1):
            ws[f'F{row}'].value = self.ex.clean_model_name(ws[f'F{row}'].value)

        self.ex.highlight_column(
            col='F', light_color=self.light_blue_fill, ws=ws, start_row=2, last_row=ws.max_row)

        print("12단계: F열 ' 개' 제거 + 조건부 하이라이트 완료")
    

    def _step_13(self, ws):
        """
        [13단계] 모든 시트에 서식 적용
        """ 
        # A열 수식 값 변환
        self.ex.set_row_number(ws)

        # 테두리 제거 & 격자 제거
        self.ex.clear_borders(ws)
        
        # D열 수식 활성화 및 채우기
        self._step_9(ws)

        # 기본 폰트 적용
        self.ex.set_basic_format(ws=ws, header_rgb="008000")

        # A, B, D, E, G열 정렬
        self.ex.set_column_alignment(ws)

        # M, P, Q, W 숫자 변환
        self._step_10(ws)

        # L열 처리
        self._step_11(ws)

        # F열 처리
        self._step_12(ws)
        

        print(f"13단계: {ws.title} 시트에 서식 적용 완료")

