import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border
import re

def zigzag_merge_packaging(file_path):
    wb = openpyxl.load_workbook(file_path)
    ws = wb.active

    headers = [cell.value for cell in ws[1]]
    data = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        data.append(list(row))
    df = pd.DataFrame(data, columns=headers)

    # 2. A열 번호 매기기 (수식 대신 값)
    df.iloc[:, 0] = range(1, len(df) + 1)

    # 3. M열 정수 변환
    if 'M' in df.columns:
        df['M'] = pd.to_numeric(df['M'], errors='coerce').fillna(0).astype(int)

    # 4. VLOOKUP(M열 → Sheet1!A:B) → V열
    if 'Sheet1' in wb.sheetnames and 'M' in df.columns:
        ws_lookup = wb['Sheet1']
        lookup_data = {
            str(row[0].value): row[1].value
            for row in ws_lookup.iter_rows(min_row=2, min_col=1, max_col=2)
            if row[0].value is not None
        }
        df['V'] = df['M'].astype(str).map(lookup_data).fillna('')

    # 5. D열 수식 = U + V
    if 'D' in df.columns and 'U' in df.columns and 'V' in df.columns:
        df['D'] = df['U'].fillna(0).astype(float) + df['V'].fillna(0).astype(float)

    # 6. F열 " 1개" 제거
    if 'F' in df.columns:
        df['F'] = df['F'].astype(str).str.replace(' 1개', '')

    # 7. 정렬: C → B 기준 오름차순
    if 'C' in df.columns and 'B' in df.columns:
        df.sort_values(by=['C', 'B'], inplace=True)

    # 8. DataFrame → 엑셀 반영
    for row in ws['A2':f'{openpyxl.utils.get_column_letter(ws.max_column)}{ws.max_row}']:
        for cell in row:
            cell.value = None
    for r_idx, row in enumerate(df.itertuples(index=False), 2):
        for c_idx, value in enumerate(row, 1):
            ws.cell(row=r_idx, column=c_idx, value=value)

    # 9. 서식 적용
    font = Font(name='맑은 고딕', size=9)
    green_fill = PatternFill(start_color="006100", end_color="006100", fill_type="solid")
    for row in ws.iter_rows():
        for cell in row:
            cell.font = font
            cell.border = Border()  # 5단계: 테두리 제거
            cell.fill = PatternFill(fill_type=None)  # 5단계: 배경색 제거
        ws.row_dimensions[cell.row].height = 15
    for cell in ws[1]:
        cell.fill = green_fill
        cell.alignment = Alignment(horizontal='center')

    # 조건부 서식: F열 강조
    blue_fill = PatternFill(start_color="CCE8FF", end_color="CCE8FF", fill_type="solid")
    regex_exact = re.compile(r'^\d+개?$', re.IGNORECASE)
    regex_repeat = re.compile(r'(\d+개\s*){2,}', re.IGNORECASE)
    if 'F' in df.columns:
        f_col = df.columns.get_loc('F') + 1
        for i in range(2, ws.max_row+1):
            f_val = str(ws.cell(row=i, column=f_col).value)
            if regex_exact.match(f_val) or regex_repeat.search(f_val):
                ws.cell(row=i, column=f_col).fill = blue_fill

    # 정렬 적용
    center_alignment = Alignment(horizontal='center')
    right_alignment = Alignment(horizontal='right')
    for col in ['A', 'B']:
        for cell in ws[col]:
            cell.alignment = center_alignment
    for col in ['D', 'E', 'G']:
        for cell in ws[col]:
            cell.alignment = right_alignment

    # 10. 시트 분할 (OK / IY)
    for sheet_name in ['OK', 'IY']:
        if sheet_name in wb.sheetnames:
            del wb[sheet_name]
    ws_ok = wb.create_sheet('OK')
    ws_iy = wb.create_sheet('IY')

    def extract_brand(value):
        match = re.search(r'\[(.*?)\]', str(value))
        return match.group(1) if match else ''

    for ws_dest, brand in [(ws_ok, '오케이마트'), (ws_iy, '아이예스')]:
        brand_rows = df[df['사이트'].astype(str).str.contains(rf'\[{brand}\]')]
        for col_idx, col in enumerate(df.columns, 1):
            ws_dest.cell(row=1, column=col_idx, value=col)
        for r_idx, row in enumerate(brand_rows.itertuples(index=False), 2):
            for c_idx, value in enumerate(row, 1):
                ws_dest.cell(row=r_idx, column=c_idx, value=value)

    # 저장
    output_path = file_path.replace('.xlsx', '_processed.xlsx')
    wb.save(output_path)
    print(f"지그재그 합포장 자동화 완료! 처리된 파일: {output_path}")
    return output_path

if __name__ == "__main__":
    excel_file_path = "/Users/smith/Documents/github/OKMart/sabangnet_API/files/test-[기본양식]-합포장용.xlsx"
    processed_file = zigzag_merge_packaging(excel_file_path)
    print("모든 처리가 완료되었습니다!")