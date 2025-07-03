import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
import re
from collections import defaultdict

def ali_merge_packaging(file_path):
    # 1. 엑셀 파일 로드 및 DataFrame 변환
    wb = openpyxl.load_workbook(file_path)
    ws = wb.active
    headers = [cell.value for cell in ws[1]]
    data = []
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row, values_only=True):
        data.append(list(row))
    df = pd.DataFrame(data, columns=headers)

    # 2. 정렬(B, C)
    if 'B' in df.columns and 'C' in df.columns:
        df = df.sort_values(by=['B', 'C'])

    # 3. A열 순번
    df.iloc[:, 0] = range(1, len(df) + 1)

    # 4. F열: Z열 복사 후 수량 패턴 정리 및 '/'를 '+'로, " 1개" 제거
    if 'Z' in df.columns and 'F' in df.columns:
        df['F'] = df['Z'].astype(str)
        df['F'] = df['F'].str.replace('/', ' + ').str.replace(';', ' + ')
        df['F'] = df['F'].apply(lambda x: re.sub(r'\* ?(\d+)', lambda m: '' if m.group(1)=='1' else f' {m.group(1)}개', x))
        df['F'] = df['F'].str.replace(' 1개', '')

    # 5. 전화번호 포맷(I→H)
    def format_phone(val):
        val = str(val or '').replace('-', '')
        if val.startswith('10'):
            val = '0' + val
        if len(val) == 11 and val.isdigit():
            return f"{val[:3]}-{val[3:7]}-{val[7:]}"
        return val
    if 'I' in df.columns and 'H' in df.columns:
        df['I'] = df['I'].apply(format_phone)
        df['H'] = df['I']

    # 6. F열: LEFT(E,16)
    if 'E' in df.columns and 'F' in df.columns:
        df['F'] = df['E'].astype(str).str[:16]

    # 7. D열: 항상 U+V로 덮어쓰기 (U/V가 없으면 0)
    if 'D' in df.columns:
        u = df['U'] if 'U' in df.columns else 0
        v = df['V'] if 'V' in df.columns else 0
        df['D'] = pd.to_numeric(u, errors='coerce').fillna(0) + pd.to_numeric(v, errors='coerce').fillna(0)

    # 8. DataFrame을 엑셀에 다시 기록 (컬럼 순서 headers 고정)
    for row in ws['A2':f'{openpyxl.utils.get_column_letter(ws.max_column)}{ws.max_row}']:
        for cell in row:
            cell.value = None
    for r_idx, row in enumerate(df[headers].itertuples(index=False), 2):
        for c_idx, value in enumerate(row, 1):
            ws.cell(row=r_idx, column=c_idx, value=value)

    # 9. 서식 및 조건부 서식 적용
    font = Font(name='맑은 고딕', size=9)
    green_fill = PatternFill(start_color="006100", end_color="006100", fill_type="solid")
    for row in ws.iter_rows():
        for cell in row:
            cell.font = font
        ws.row_dimensions[cell.row].height = 15
    for cell in ws[1]:
        cell.fill = green_fill
    # F열 파란색 배경(정규식 패턴)
    blue_fill = PatternFill(start_color="CCE8FF", end_color="CCE8FF", fill_type="solid")
    regex_exact = re.compile(r'^\d+개?$', re.IGNORECASE)
    regex_repeat = re.compile(r'(\d+개\s*){2,}', re.IGNORECASE)
    if 'F' in df.columns:
        f_col = df.columns.get_loc('F') + 1
        for i in range(2, ws.max_row+1):
            f_val = str(ws.cell(row=i, column=f_col).value)
            if regex_exact.match(f_val) or regex_repeat.search(f_val):
                ws.cell(row=i, column=f_col).fill = blue_fill
    # A, B 가운데 정렬, D, E, G 오른쪽 정렬
    center_alignment = Alignment(horizontal='center')
    right_alignment = Alignment(horizontal='right')
    for col in ['A', 'B']:
        for cell in ws[col]:
            cell.alignment = center_alignment
    for col in ['D', 'E', 'G']:
        for cell in ws[col]:
            cell.alignment = right_alignment
    for cell in ws[1]:
        cell.alignment = center_alignment

    # 19. "품절" 텍스트 강조 및 F열 수정
    if 'J' in df.columns and 'F' in df.columns:
        j_col_idx = df.columns.get_loc('J') + 1
        f_col_idx = df.columns.get_loc('F') + 1
        for i in range(2, ws.max_row + 1):
            j_val = str(ws.cell(row=i, column=j_col_idx).value or '')
            if '품절' in j_val:
                cell_j = ws.cell(row=i, column=j_col_idx)
                cell_j.font = Font(color='FF0000', bold=True)
                f_cell = ws.cell(row=i, column=f_col_idx)
                if '[3000원 환불처리]' not in str(f_cell.value):
                    f_cell.value = str(f_cell.value) + ' [3000원 환불처리]'
                f_cell.fill = blue_fill

    # 21. Sheet1 기반 VLOOKUP → S열
    try:
        ws_lookup = wb['Sheet1']
        lookup_data = [(row[0].value, row[1].value) for row in ws_lookup.iter_rows(min_row=2, max_row=ws_lookup.max_row, min_col=1, max_col=2)]
        lookup_dict = {str(k): v for k, v in lookup_data if k is not None}
        s_col_values = []
        for val in df['F']:
            s_val = lookup_dict.get(str(val), 'S')
            s_col_values.append(s_val)
        df['S'] = s_col_values
        if 'S' not in headers:
            headers.append('S')
    except Exception as e:
        print(f"Sheet1에서 VLOOKUP 처리 중 오류 발생: {e}")

    # 22. 브랜드별 시트 분리
    ok_rows = df[df['사이트'].astype(str).str.contains('오케이마트', na=False)]
    iy_rows = df[df['사이트'].astype(str).str.contains('아이예스', na=False)]

    for sheet_name in ['OK', 'IY']:
        if sheet_name in wb.sheetnames:
            del wb[sheet_name]
    ws_ok = wb.create_sheet('OK')
    ws_iy = wb.create_sheet('IY')

    def write_to_sheet(ws_target, df_data):
        for col_idx, col in enumerate(headers, 1):
            ws_target.cell(row=1, column=col_idx, value=col)
        for r_idx, row in enumerate(df_data[headers].itertuples(index=False), 2):
            for c_idx, value in enumerate(row, 1):
                ws_target.cell(row=r_idx, column=c_idx, value=value)

    write_to_sheet(ws_ok, ok_rows)
    write_to_sheet(ws_iy, iy_rows)

    # 24. 시트 순서 재배치
    desired_order = ['Sheet', 'OK', 'IY', 'Sheet1']
    existing_sheets = wb.sheetnames
    for name in reversed(desired_order):
        if name in existing_sheets:
            sheet = wb[name]
            wb._sheets.remove(sheet)
            wb._sheets.insert(0, sheet)

    # 저장
    output_path = file_path.replace('.xlsx', '_processed.xlsx')
    wb.save(output_path)
    print(f"알리 합포장 자동화 완료! 처리된 파일: {output_path}")
    return output_path

# 사용 예시
if __name__ == "__main__":
    excel_file_path = "/Users/smith/Documents/github/OKMart/sabangnet_API/files/test-[기본양식]-합포장용.xlsx"
    processed_file = ali_merge_packaging(excel_file_path)
    print("모든 처리가 완료되었습니다!")