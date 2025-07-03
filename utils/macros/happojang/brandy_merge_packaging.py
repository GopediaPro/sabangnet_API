import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from collections import defaultdict
import re

def brandy_merge_packaging(file_path):
    wb = openpyxl.load_workbook(file_path)
    ws = wb.active

    headers = [cell.value for cell in ws[1]]
    data = [[cell.value for cell in row] for row in ws.iter_rows(min_row=2, max_row=ws.max_row)]
    df = pd.DataFrame(data, columns=headers)

    # 1. 서식 설정 (폰트, 행 높이)
    font = Font(name='맑은 고딕', size=9)
    green_fill = PatternFill(start_color="006100", end_color="006100", fill_type="solid")
    for row in ws.iter_rows():
        for cell in row:
            cell.font = font
        ws.row_dimensions[cell.row].height = 15
    for cell in ws[1]:
        cell.fill = green_fill

    # 2. D열 수식 (U + V)
    if 'D' in df.columns and 'U' in df.columns and 'V' in df.columns:
        df['D'] = pd.to_numeric(df['U'], errors='coerce').fillna(0) + pd.to_numeric(df['V'], errors='coerce').fillna(0)

    # 3. D열 값 고정 (이미 적용됨 - 수식이 아닌 값)
    # 생략 가능

    # 4~6. C+J 그룹 기준 금액 합산 + 모델명 병합 + 중복행 삭제
    if 'C' in df.columns and 'J' in df.columns:
        group_dict = defaultdict(list)
        for idx, row in df.iterrows():
            key = f"{row['C']}|{row['J']}"
            group_dict[key].append(idx)
        drop_indices = []
        for key, rows in group_dict.items():
            if len(rows) > 1:
                total = sum(pd.to_numeric(df.at[r, 'D'], errors='coerce') for r in rows)
                models = [str(df.at[r, 'F']) for r in rows if pd.notna(df.at[r, 'F'])]
                df.at[rows[0], 'D'] = total
                df.at[rows[0], 'F'] = ' + '.join(models)
                drop_indices.extend(rows[1:])
        df.drop(index=drop_indices, inplace=True)
        df.reset_index(drop=True, inplace=True)

    # 7. F열 " 1개" 제거
    if 'F' in df.columns:
        df['F'] = df['F'].astype(str).str.replace(' 1개', '')

    # 8. 셀 배경 제거
    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.fill = PatternFill(fill_type=None)

    # 9. 전화번호 포맷 (H, I)
    def format_phone(val):
        val = str(val or '').replace('-', '')
        if len(val) == 11 and val.startswith('010') and val.isdigit():
            return f"{val[:3]}-{val[3:7]}-{val[7:]}"
        return val
    for col in ['H', 'I']:
        if col in df.columns:
            df[col] = df[col].apply(format_phone)

    # 10. A열 순번 수식
    for i in range(2, ws.max_row + 1):
        ws.cell(row=i, column=1).value = f"=ROW()-1"

    # 11. 테두리 제거
    from openpyxl.styles.borders import Border
    no_border = Border()
    for row in ws.iter_rows():
        for cell in row:
            cell.border = no_border

    # 12. J열에 '제주' 포함 시 처리
    if all(col in df.columns for col in ['F', 'J']):
        f_idx = df.columns.get_loc('F') + 1
        j_idx = df.columns.get_loc('J') + 1
        for i in range(2, ws.max_row + 1):
            j_val = str(ws.cell(row=i, column=j_idx).value or '')
            if '제주' in j_val:
                f_cell = ws.cell(row=i, column=f_idx)
                if '[3000원 연락해야함]' not in str(f_cell.value):
                    f_cell.value = str(f_cell.value) + ' [3000원 연락해야함]'
                f_cell.fill = PatternFill(start_color="DDEBF7", end_color="DDEBF7", fill_type="solid")
                j_cell = ws.cell(row=i, column=j_idx)
                j_cell.font = Font(color='FF0000', bold=True)

    # 13. 열 정렬
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

    # 14. D열 기준 오름차순 정렬
    df.sort_values(by='금액', ascending=True, inplace=True)
    df.reset_index(drop=True, inplace=True)

    # DataFrame 다시 기록
    for row in ws['A2':f'{openpyxl.utils.get_column_letter(ws.max_column)}{ws.max_row}']:
        for cell in row:
            cell.value = None
    for r_idx, row in enumerate(df.itertuples(index=False), 2):
        for c_idx, value in enumerate(row, 1):
            ws.cell(row=r_idx, column=c_idx, value=value)

    # 저장
    output_path = file_path.replace('.xlsx', '_processed.xlsx')
    wb.save(output_path)
    print(f"브랜디 합포장 자동화 완료! 처리된 파일: {output_path}")
    return output_path

if __name__ == "__main__":
    excel_file_path = "/Users/smith/Documents/github/OKMart/sabangnet_API/files/test-[기본양식]-합포장용.xlsx"
    processed_file = brandy_merge_packaging(excel_file_path)
    print("모든 처리가 완료되었습니다!")