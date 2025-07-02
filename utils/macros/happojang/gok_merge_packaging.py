import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
import re
from collections import defaultdict

def gok_merge_packaging(file_path):
    # 1. 엑셀 파일 로드 및 DataFrame 변환
    wb = openpyxl.load_workbook(file_path)
    ws = wb.active
    headers = [cell.value for cell in ws[1]]
    data = []
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row, values_only=True):
        data.append(list(row))
    df = pd.DataFrame(data, columns=headers)
    # 2. A열 번호 매기기
    df.iloc[:, 0] = range(1, len(df) + 1)
    # 3. P열 '/' 분할 후 합산
    if 'P' in df.columns:
        def sum_split(val):
            if pd.isna(val): return val
            parts = [float(x) for x in str(val).split('/') if x.strip().isdigit()]
            return sum(parts) if parts else val
        df['P'] = df['P'].apply(sum_split)
    # 4. V열 '/' 분할 후 모두 같으면 첫 값, 다르면 0
    if 'V' in df.columns:
        def unify_split(val):
            if pd.isna(val): return val
            parts = [int(x) for x in str(val).split('/') if x.strip().isdigit() and int(x)!=0]
            if not parts:
                return 0
            elif len(set(parts)) == 1:
                return parts[0]
            else:
                return parts[0]
        df['V'] = df['V'].apply(unify_split)
    # 5. F열 '/'를 '+'로, ' 1개' 제거
    if 'F' in df.columns:
        df['F'] = df['F'].astype(str).str.replace('/', ' + ').str.replace(' 1개', '')
    # 6. F열 LEFT(E,10)로 대체
    if 'E' in df.columns and 'F' in df.columns:
        df['F'] = df['E'].astype(str).str[:10]
    # 7. D열 수식 적용 (예: D = U + V)
    if 'D' in df.columns and 'U' in df.columns and 'V' in df.columns:
        df['D'] = df['U'].fillna(0).astype(float) + df['V'].fillna(0).astype(float)
    # 8. DataFrame을 엑셀에 다시 기록
    for row in ws['A2':f'{openpyxl.utils.get_column_letter(ws.max_column)}{ws.max_row}']:
        for cell in row:
            cell.value = None
    for r_idx, row in enumerate(df.itertuples(index=False), 2):
        for c_idx, value in enumerate(row, 1):
            ws.cell(row=r_idx, column=c_idx, value=value)
    # 9. 서식 및 조건부 서식 적용
    font = Font(name='맑은 고딕', size=9)
    green_fill = PatternFill(start_color="00B050", end_color="00B050", fill_type="solid")
    for row in ws.iter_rows():
        for cell in row:
            cell.font = font
        ws.row_dimensions[cell.row].height = 15
    for cell in ws[1]:
        cell.fill = green_fill
    blue_fill = PatternFill(start_color="CCE8FF", end_color="CCE8FF", fill_type="solid")
    regex_exact = re.compile(r'^\d+개?$', re.IGNORECASE)
    regex_repeat = re.compile(r'(\d+개\s*){2,}', re.IGNORECASE)
    if 'F' in df.columns:
        f_col = df.columns.get_loc('F') + 1
        for i in range(2, ws.max_row+1):
            f_val = str(ws.cell(row=i, column=f_col).value)
            if regex_exact.match(f_val) or regex_repeat.search(f_val):
                ws.cell(row=i, column=f_col).fill = blue_fill
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

    # 9. A열 순번 수식 (=ROW()-1)
    for i in range(2, ws.max_row + 1):
        ws.cell(row=i, column=1).value = f"=ROW()-1"

    # 10. 정렬: C → B 기준
    if 'C' in df.columns and 'B' in df.columns:
        df.sort_values(by=['C', 'B'], inplace=True)
        df.reset_index(drop=True, inplace=True)

    # DataFrame을 다시 엑셀에 반영 (정렬 후)
    for row in ws['A2':f'{openpyxl.utils.get_column_letter(ws.max_column)}{ws.max_row}']:
        for cell in row:
            cell.value = None
    for r_idx, row in enumerate(df.itertuples(index=False), 2):
        for c_idx, value in enumerate(row, 1):
            ws.cell(row=r_idx, column=c_idx, value=value)

    # 11. 셀 배경색 및 테두리 제거
    from openpyxl.styles import Border
    for row in ws.iter_rows():
        for cell in row:
            cell.fill = PatternFill(fill_type=None)
            cell.border = Border()

    # 12. L열 내용 삭제
    if 'L' in df.columns:
        l_col = df.columns.get_loc('L') + 1
        for i in range(2, ws.max_row + 1):
            ws.cell(row=i, column=l_col).value = None

    # 13. 계정명 기준 시트 분리
    def extract_account_name(text):
        match = re.search(r'\[(.*?)\]', str(text))
        return match.group(1) if match else ''

    site_groups = {
        'OK,CL,BB': ['오케이마트', '클로버프', '베이지베이글'],
        'IY': ['아이예스']
    }

    for sheet_name, names in site_groups.items():
        if sheet_name in wb.sheetnames:
            del wb[sheet_name]
        ws_new = wb.create_sheet(title=sheet_name)
        for col_idx, col in enumerate(df.columns, 1):
            ws_new.cell(row=1, column=col_idx, value=col)

        filtered_rows = df[df['사이트'].apply(lambda x: extract_account_name(x) in names)]
        for r_idx, row in enumerate(filtered_rows.itertuples(index=False), 2):
            for c_idx, value in enumerate(row, 1):
                ws_new.cell(row=r_idx, column=c_idx, value=value)

        for c in range(1, ws.max_column + 1):
            col_letter = openpyxl.utils.get_column_letter(c)
            ws_new.column_dimensions[col_letter].width = ws.column_dimensions[col_letter].width

    output_path = file_path.replace('.xlsx', '_processed.xlsx')
    wb.save(output_path)
    print(f"G옥 합포장 자동화 완료! 처리된 파일: {output_path}")
    return output_path

# 사용 예시 (other_site_macro.py 스타일)
if __name__ == "__main__":
    # 파일 경로를 지정하세요
    excel_file_path = "/Users/smith/Documents/github/OKMart/sabangnet_API/files/test-[기본양식]-합포장용.xlsx"
    processed_file = gok_merge_packaging(excel_file_path)
    print("모든 처리가 완료되었습니다!")
