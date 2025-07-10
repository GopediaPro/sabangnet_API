import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border
from openpyxl.utils import get_column_letter
from utils.excel_handler import ExcelHandler


class AliMacro:
    def __init__(self, file_path):
        self.ex = ExcelHandler.from_file(file_path)
        self.file_path = file_path
        self.ws = self.ex.ws
        self.wb = self.ex.wb
        self.last_row = self.ws.max_row
        self.last_column = self.ws.max_column
        self.right_alignment = Alignment(horizontal='right')
        self.center_alignment = Alignment(horizontal='center')
        self.light_blue_fill = PatternFill(
            start_color="ADD8E6", end_color="ADD8E6", fill_type="solid")
        self.dark_green_fill = PatternFill(
            start_color="008000", end_color="008000", fill_type="solid")
        self.white_font = Font(name='맑은 고딕', size=9, color="FFFFFF", bold=True)
        self.headers = []
        self.df = None
        self.ws_map = {}

    def step_1_to_10(self):
        """
        1~10단계 자동화 실행
        """
        print("1~10단계 자동화 시작...")
        self._step_1()
        self._step_2()
        self._step_3()
        self._step_4()
        self._step_5()

        print("10단계: 모든 시트에 서식 적용 시작...")
        for ws in self.wb.worksheets:
            if ws.max_row <= 1:
                continue
            self._step_10(ws)

        output_path = self.ex.save_file(self.file_path)
        print(f"✓ 알리 ERP 자동화 완료! 최종 파일: {output_path}")
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

    def _step_2(self):
        """
        [2단계] Z 열 -> F 복사, 전화번호2 -> 전화번호1 복사, 열너비
        """
        # Z열 값을 F열로 복사
        for idx, row in self.df.iterrows():
            self.df.at[idx, '제품명'] = row['수집옵션']

            f_value = self.df.at[idx, '제품명']
            if f_value:
                txt = str(f_value).strip()

                # "* * 1" 패턴 처리 (끝에 " * 1"이 있는 경우)
                if txt.endswith(" * 1"):
                    self.ws[f'F{row}'].value = txt[:-4]

                # "* * 숫자" 패턴 처리
                elif " * " in txt:
                    parts = txt.split(" * ")
                    if len(parts) >= 2:
                        suffix = parts[-1].strip()
                        if suffix.isdigit() and suffix != "1":
                            # 마지막 " * 숫자" 부분을 " 숫자개"로 변경
                            base_text = " * ".join(parts[:-1])
                            self.ws[f'F{row}'].value = f"{base_text} {suffix}개"

            i_value = self.df.at[idx, '전화번호2']
            if i_value:
                phone = str(i_value).replace("-", "").strip()

                if phone.isdigit():
                    if len(phone) == 11:
                        # 11자리: 010-1234-5678 형태로 변환
                        formatted = f"{phone[:3]}-{phone[3:7]}-{phone[7:]}"
                    elif len(phone) in [9, 10]:
                        # 9~10자리: 앞에 010 추가 후 포맷
                        phone = "010" + phone[-8:]
                        formatted = f"{phone[:3]}-{phone[3:7]}-{phone[7:]}"
                    else:
                        formatted = i_value

                    i_value = formatted

                self.df.at[idx, '전화번호1'] = i_value

    def _step_3(self):
        """
        [3단계] 워크시트에 정렬된 데이터 덮어쓰기
        """
        for row_idx, row_data in enumerate(self.df.itertuples(index=False), start=2):
            for col_idx, value in enumerate(row_data, start=1):
                self.ws.cell(row=row_idx, column=col_idx,
                             value=value if value or value == 0 else "")
        print("3단계: 워크시트에 정렬된 데이터 덮어쓰기 완료")

    def _step_4(self):
        """
        [4단계] 시트 분리 준비
        """
        self.ws_map = self.ex.create_split_sheets(self.headers, ["OK", "IY"])

        self.ex.set_header_style(
            self.ws_map["OK"], self.headers, self.dark_green_fill, self.white_font, self.center_alignment)
        self.ex.set_header_style(
            self.ws_map["IY"], self.headers, self.dark_green_fill, self.white_font, self.center_alignment)

        print("4단계: 시트 분리 준비 완료")

    def _step_5(self):
        """
        [5단계] 시트 분리
        """
        site_mapping = {
            "OK": ["오케이마트"],
            "IY": ["아이예스"]
        }
        self.ex.split_sheets_by_site(self.df, self.ws_map, site_mapping)
        print("5단계: 시트 분리 완료")

    def _step_6(self, ws):
        """
        [6단계] H, F 열 너비 설정
        """
        # H열 너비를 I열과 동일하게 설정
        ws.column_dimensions['H'].width = self.ws.column_dimensions['I'].width

        # F열 너비 설정
        ws.column_dimensions['F'].width = 45

    def _step_7(self, ws):
        """
        [7단계] D열 금액 수식
        """
        # D열에 U+V 수식 입력
        d2_formula = ws['D2'].value
        self.ex.autofill_d_column(ws=ws,
                                  start_row=2, end_row=ws.max_row, formula=d2_formula)
        print("7단계: D열 수식 처리 완료")

    def _step_8(self, ws):
        """
        [8단계] M, P, Q, W 숫자 변환
        """
        cols_names = ['M', 'P', 'Q', 'W']
        self.ex.convert_numeric_strings(
            ws=ws, start_row=2, end_row=ws.max_row, cols=cols_names)
        print("8단계: M, P, Q,W 숫자 변환 완료")

    def _step_9(self, ws):
        """
        [9단계] 제주 관련 서식 적용
        """
        for row in range(2, ws.max_row + 1):
            self.ex.process_jeju_address(row=row, ws=ws)
        print("9단계: F열 모르겠는 셀 색칠음영 (하늘색) 완료")

    def _step_10(self, ws):
        """
        [10단계] 모든 시트에 서식 적용
        """
        # A열 수식 값 변환
        self.ex.set_row_number(ws)

        # H열, F열 너비 설정
        self._step_6(ws)

        # 테두리 제거 & 격자 제거
        self.ex.clear_borders(ws)

        # D열 수식 처리
        self._step_7(ws)

        # 기본 폰트 적용
        self.ex.set_basic_format(ws=ws, header_rgb="008000")

        # # M, P, Q,W 숫자 변환
        self._step_8(ws)

        # A, B, D, E, G열 정렬
        self.ex.set_column_alignment(ws)

        # 제주 관련 서식 적용
        self._step_9(ws)

        print(f"10단계: {ws.title} 시트에 서식 적용 완료")

    def _step_13(self):
        """
        [13~14단계] S열 VLOOKUP 및 값 붙여넣기 및 #N/A → "S"
        """
        # S열에 VLOOKUP 수식 입력 (임시로 "S" 값 설정)
        for row in range(2, self.last_row + 1):
            # 실제 VLOOKUP 계산은 복잡하므로 기본값 "S" 설정
            self.ws[f'S{row}'].value = "S"
            self.ws[f'S{row}'].number_format = 'General'


def process_vlookup_simulation(file_path, lookup_sheet="sheet1", lookup_range="A:B"):
    """
    VLOOKUP 시뮬레이션 함수 (실제 조회 테이블이 있는 경우 사용)

    Args:
        file_path (str): Excel 파일 경로
        lookup_sheet (str): 조회할 시트명
        lookup_range (str): 조회 범위
    """
    try:
        workbook = openpyxl.load_workbook(file_path)

        # 조회 테이블이 있는지 확인
        if lookup_sheet in workbook.sheetnames:
            lookup_ws = workbook[lookup_sheet]

            # 실제 VLOOKUP 로직 구현
            for ws_name in workbook.sheetnames:
                ws = workbook[ws_name]
                if ws.max_row > 1:
                    for row in range(2, ws.max_row + 1):
                        f_value = ws[f'F{row}'].value
                        if f_value:
                            # 조회 로직 (간단한 예시)
                            lookup_result = "S"  # 기본값

                            # 실제 조회 테이블에서 값 찾기
                            for lookup_row in range(1, lookup_ws.max_row + 1):
                                lookup_key = lookup_ws[f'A{lookup_row}'].value
                                if lookup_key and str(lookup_key).strip() == str(f_value).strip():
                                    lookup_result = lookup_ws[f'B{lookup_row}'].value or "S"
                                    break

                            ws[f'S{row}'].value = lookup_result

            workbook.save(file_path)
            print("VLOOKUP 시뮬레이션 완료")
        else:
            print(f"조회 시트 '{lookup_sheet}'를 찾을 수 없습니다.")

    except Exception as e:
        print(f"VLOOKUP 처리 중 오류: {e}")
