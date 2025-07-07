import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border
import re

"""
주문관리 Excel 파일 매크로 공통 처리 메소드
- 기본 서식 설정
- 수식 처리
- 데이터 정리
- 정렬 및 레이아웃
- 특수 처리 (제주도 주소, 결제방식 등)
"""


# 기본 서식 설정 Method
def set_basic_format(ws, header_rgb="006100"):
    """
    폰트, 행높이, 첫 행 배경색, 줄바꿈 해제 등 기본 서식 적용
    예시:
        wb = openpyxl.load_workbook('file.xlsx')
        ws = wb.active
        set_basic_format(ws)
    """
    font = Font(name='맑은 고딕', size=9)
    green_fill = PatternFill(start_color=header_rgb, end_color=header_rgb, fill_type="solid")
    for row in ws.iter_rows():
        for cell in row:
            cell.font = font
            cell.alignment = Alignment(wrap_text=False)
        ws.row_dimensions[row[0].row].height = 15
    for cell in ws[1]:
        cell.fill = green_fill
        cell.alignment = Alignment(horizontal='center')

# 수식 처리 Method
def autofill_d_column(ws, start_row=2, end_row=None, formula=None):
    """
    D열 수식 활성화 및 복사 (금액 계산)
    예시:
        autofill_d_column(ws, 2, last_row, "=U{row}+V{row}")
    - formula에 "{row}"를 포함하면 각 행 번호로 치환하여 적용
    """
    if not end_row:
        end_row = ws.max_row
    if not formula:
        formula = ws['D2'].value
    for row in range(start_row, end_row + 1):
        if isinstance(formula, str) and '{row}' in formula:
            ws[f'D{row}'].value = formula.format(row=row)
        elif isinstance(formula, str) and '=' in formula:
            ws[f'D{row}'].value = formula.replace('2', str(row))
        else:
            ws[f'D{row}'].value = formula

def set_row_number(ws, start_row=2, end_row=None):
    """
    A열 순번 자동 생성 (=ROW()-1)
    예시:
        set_row_number(ws)
    """
    if not end_row:
        end_row = ws.max_row
    for row in range(start_row, end_row + 1):
        ws[f"A{row}"].value = "=ROW()-1"

def convert_formula_to_value(ws):
    """
    수식 → 값 변환 처리 (모든 시트)
    (openpyxl은 수식 결과값을 계산하지 않으므로, 실제 값 변환은 Excel에서 복사-값붙여넣기로 처리)
    예시:
        convert_formula_to_value(ws)
    """
    for row in ws.iter_rows():
        for cell in row:
            if cell.value and isinstance(cell.value, str) and cell.value.startswith('='):
                # 실제 계산은 Excel에서, 여기선 수식 문자열만 제거
                cell.value = cell.value

# 데이터 정리 Method
def clear_borders(ws):
    """
    테두리 제거
    예시:
        clear_borders(ws)
    """
    for row in ws.iter_rows():
        for cell in row:
            cell.border = Border()

def clear_fills(ws):
    """
    배경색 제거
    예시:
        clear_fills(ws)
    """
    for row in ws.iter_rows():
        for cell in row:
            cell.fill = PatternFill(fill_type=None)

def format_phone_number(val):
    """
    전화번호 11자리 → 010-0000-0000 형식
    예시:
        ws['H2'].value = format_phone_number(ws['H2'].value)
    """
    val = str(val or '').replace('-', '').strip()
    if len(val) == 11 and val.startswith('010') and val.isdigit():
        return f"{val[:3]}-{val[3:7]}-{val[7:]}"
    return val

def clean_model_name(val):
    """
    모델명에서 ' 1개' 텍스트 제거
    예시:
        ws['F2'].value = clean_model_name(ws['F2'].value)
    """
    return str(val).replace(' 1개', '') if val else val

def sum_prow_with_slash(ws):
    """
    P열 "/" 금액 합산
    예시:
        sum_prow_with_slash(ws)
    """
    last_row = ws.max_row
    for r in range(2, last_row + 1):
        p_raw = str(ws[f"P{r}"].value or "")
        if "/" in p_raw:
            nums = [float(n) for n in p_raw.split("/") if n.strip().isdigit()]
            ws[f"P{r}"].value = sum(nums) if nums else 0
        else:
            ws[f"P{r}"].value = to_num(p_raw)

def to_num(val) -> float:
    """
    '12,345원' → 12345.0 (실패 시 0)
    예시:
        num = to_num("12,345원")
    """
    try:
        return float(re.sub(r"[^\d.-]", "", str(val))) if str(val).strip() else 0.0
    except ValueError:
        return 0.0

# 정렬 및 레이아웃 Method
def set_column_alignment(ws):
    """
    A,B(가운데), D,E,G(오른쪽), 첫 행 가운데 정렬
    예시:
        set_column_alignment(ws)
    """
    center = Alignment(horizontal='center')
    right = Alignment(horizontal='right')
    for cell in ws['A']:
        cell.alignment = center
    for cell in ws['B']:
        cell.alignment = center
    for cell in ws['D']:
        cell.alignment = right
    for cell in ws['E']:
        cell.alignment = right
    for cell in ws['G']:
        cell.alignment = right
    for cell in ws[1]:
        cell.alignment = center

def sort_dataframe_by_c_b(df):
    """
    DataFrame을 C열 → B열 순서로 오름차순 정렬
    예시:
        df = sort_dataframe_by_c_b(df)
    """
    if 'C' in df.columns and 'B' in df.columns:
        return df.sort_values(by=['C', 'B']).reset_index(drop=True)
    return df

# 특수 처리 Method
def process_jeju_address(ws, row, f_col='F', j_col='J'):
    """
    제주도 주소: '[3000원 연락해야함]' 추가, 연한 파란색 배경 및 빨간 글씨 적용
    예시:
        process_jeju_address(ws, row=5)
    """
    red_font = Font(color="FF0000", bold=True)
    # RGB(204,255,255) → hex: "CCFFFF"
    light_blue_fill = PatternFill(start_color="CCFFFF", end_color="CCFFFF", fill_type="solid")
    # F열 안내문 추가
    f_val = ws[f'{f_col}{row}'].value
    if f_val and "[3000원 연락해야함]" not in str(f_val):
        ws[f'{f_col}{row}'].value = str(f_val) + " [3000원 연락해야함]"
    # J열 빨간 글씨
    ws[f'{j_col}{row}'].font = red_font
    # F열 연한 파란색 배경
    ws[f'{f_col}{row}'].fill = light_blue_fill

def process_l_column(ws, row, l_col='L'):
    """
    L열 결제방식: '신용' 삭제, '착불' 빨간 글씨
    예시:
        process_l_column(ws, row=7)
    """
    red_font = Font(color="FF0000", bold=True)
    l_val = ws[f'{l_col}{row}'].value
    if l_val == "신용":
        ws[f'{l_col}{row}'].value = ""
    elif l_val == "착불":
        ws[f'{l_col}{row}'].font = red_font
