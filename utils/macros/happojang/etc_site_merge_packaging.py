import pandas as pd
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill
import re
from collections import defaultdict

def etc_site_merge_packaging(file_path):
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
    df.reset_index(drop=True, inplace=True)
    # 3. A열 번호 매기기
    df.iloc[:, 0] = range(1, len(df) + 1)
    # 4. 조건별 배송비, 금액 처리 (V, U, B, X 등)
    for idx, row in df.iterrows():
        site = str(row['B']) if 'B' in df.columns else ''
        order = str(row['X']) if 'X' in df.columns else ''
        shipping = row['V'] if 'V' in df.columns else 0
        amount = row['U'] if 'U' in df.columns else 0
        if any(x in site for x in ['이랜드', '롯데ON', '롯데닷컴', '현대몰']) and '/' in order:
            order_count = order.count('/') + 1
            if pd.notna(shipping) and shipping > 3000:
                df.at[idx, 'V'] = round(shipping / order_count)
        if '롯데ON' in site:
            df.at[idx, 'V'] = 0
        if '현대몰' in site:
            if pd.notna(amount) and amount > 30000:
                df.at[idx, 'V'] = 0
            else:
                df.at[idx, 'V'] = 3000
    # 5. 전화번호 포맷(H, I)
    def format_phone(val):
        val = str(val or '').replace('-', '').strip()
        if len(val) == 11 and val.startswith('010') and val.isdigit():
            return f"{val[:3]}-{val[3:7]}-{val[7:]}"
        return val
    for col in ['H', 'I']:
        if col in df.columns:
            df[col] = df[col].apply(format_phone)
    # 6. 주문번호 자르기 (F열 임시 사용)
    if 'B' in df.columns and 'E' in df.columns:
        def cut_order(row):
            site = str(row['B'])
            order_val = str(row['E'])
            if 'YES24' in site:
                return order_val[:11]
            elif 'CJ대한통운' in site:
                return order_val[:26]
            elif 'GSSHOP' in site:
                return order_val[:21]
            elif '롯데닷컴' in site:
                return order_val[:16]
            elif '인터파크' in site:
                return order_val[:13]
            elif '우체국' in site:
                return order_val[:36]
            elif '카카오톡딜' in site or '카카오현대몰' in site:
                return order_val[:10]
            else:
                return order_val
        df['F'] = df.apply(cut_order, axis=1)
        df['E'] = df['F']
    # 7. F열 " 1개" 제거, "/"를 "+"로 변경
    if 'F' in df.columns:
        df['F'] = df['F'].astype(str).str.replace(' 1개', '').str.replace('/', ' + ')
    # 8. D열 수식 적용 (예: D = U + V)
    if 'D' in df.columns and 'U' in df.columns and 'V' in df.columns:
        df['D'] = df['U'].fillna(0).astype(float) + df['V'].fillna(0).astype(float)

    # 2. D열 수식 활성화 및 복사 (단순히 D = U + V 이미 처리됨, 여기선 수식 적용 의미 아님)

    # 9. DataFrame을 엑셀에 다시 기록
    for row in ws['A2':f'{openpyxl.utils.get_column_letter(ws.max_column)}{ws.max_row}']:
        for cell in row:
            cell.value = None
    for r_idx, row in enumerate(df.itertuples(index=False), 2):
        for c_idx, value in enumerate(row, 1):
            ws.cell(row=r_idx, column=c_idx, value=value)
    # 10. 서식 및 조건부 서식 적용
    font = Font(name='맑은 고딕', size=9)
    green_fill = PatternFill(start_color="006100", end_color="006100", fill_type="solid")
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
    # 14. 셀 배경색 제거
    for row in ws.iter_rows():
        for cell in row:
            cell.fill = PatternFill(fill_type=None)

    # 15. 전체 테두리 제거
    from openpyxl.styles.borders import Border
    no_border = Border()
    for row in ws.iter_rows():
        for cell in row:
            cell.border = no_border

    # 19. L열 '정상', '품절' 처리
    if 'L' in df.columns:
        l_col_idx = df.columns.get_loc('L') + 1
        for i in range(2, ws.max_row + 1):
            cell = ws.cell(row=i, column=l_col_idx)
            if cell.value == '품절':
                cell.font = Font(color='FF0000', bold=True)
            elif cell.value == '정상':
                cell.font = Font(color='FF0000', bold=True)

    # 20. B에 '카카오', J에 '품절' 포함시 F 수정 및 J 강조
    if all(col in df.columns for col in ['B', 'F', 'J']):
        b_idx = df.columns.get_loc('B') + 1
        f_idx = df.columns.get_loc('F') + 1
        j_idx = df.columns.get_loc('J') + 1
        for i in range(2, ws.max_row + 1):
            b_val = str(ws.cell(row=i, column=b_idx).value or '')
            j_val = str(ws.cell(row=i, column=j_idx).value or '')
            if '카카오' in b_val and '품절' in j_val:
                f_cell = ws.cell(row=i, column=f_idx)
                if '[3000원 환불처리]' not in str(f_cell.value):
                    f_cell.value = str(f_cell.value) + ' [3000원 환불처리]'
                f_cell.fill = PatternFill(start_color="CCFFFF", end_color="CCFFFF", fill_type="solid")
                j_cell = ws.cell(row=i, column=j_idx)
                j_cell.font = Font(color='FF0000', bold=True)

    # 21. 정렬
    for col in ['A', 'B']:
        for cell in ws[col]:
            cell.alignment = Alignment(horizontal='center')
    for col in ['D', 'E', 'G']:
        for cell in ws[col]:
            cell.alignment = Alignment(horizontal='right')
    for cell in ws[1]:
        cell.alignment = Alignment(horizontal='center')

    # 5. 줄바꿈 해제
    for row in ws.iter_rows():
        for cell in row:
            cell.alignment = Alignment(wrap_text=False, horizontal=cell.alignment.horizontal if cell.alignment else None)

    # 13. 특정 사이트 주문번호 숫자 서식 변환
    numeric_sites = ['에이블리', '오늘의집', '쿠팡', '텐바이텐', 'NS홈쇼핑', '그립', '보리보리', '카카오선물하기', '톡스토어', '토스']
    if '' in df.columns and 'E' in df.columns:
        for idx, row in df.iterrows():
            site = str(row['B'])
            if any(keyword in site for keyword in numeric_sites):
                try:
                    df.at[idx, 'E'] = int(re.sub(r'\D', '', str(row['E'])))
                except:
                    pass

    # 22. 시트 분리: 정확한 계정명 기준 (B 열 [브랜드명] 형태에서 추출)
    def extract_account_name(val):
        match = re.search(r'\[(.*?)\]', str(val))
        return match.group(1) if match else ''

    site_map = {
        '오케이마트': 'OK',
        '아이예스': 'IY',
        '베이지베이글': 'BB',
    }
    for brand, sheet_name in site_map.items():
        filtered = df[df['사이트'].apply(lambda x: extract_account_name(x) == brand)]
        if sheet_name in wb.sheetnames:
            del wb[sheet_name]
        ws_new = wb.create_sheet(title=sheet_name)
        for col_idx, col in enumerate(df.columns, 1):
            ws_new.cell(row=1, column=col_idx, value=col)
        for r_idx, row in enumerate(filtered.itertuples(index=False), 2):
            for c_idx, value in enumerate(row, 1):
                ws_new.cell(row=r_idx, column=c_idx, value=value)
        # A열 순번 재설정
        for i in range(2, 2 + len(filtered)):
            ws_new.cell(row=i, column=1).value = i - 1
        # 열너비 복사
        for c in range(1, ws.max_column + 1):
            ws_new.column_dimensions[openpyxl.utils.get_column_letter(c)].width = ws.column_dimensions[openpyxl.utils.get_column_letter(c)].width

    output_path = file_path.replace('.xlsx', '_processed.xlsx')
    wb.save(output_path)
    print(f"기타사이트 합포장 자동화 완료! 처리된 파일: {output_path}")
    return output_path

# 사용 예시 (other_site_macro.py 스타일)
if __name__ == "__main__":
    # 파일 경로를 지정하세요
    excel_file_path = "/Users/smith/Documents/github/OKMart/sabangnet_API/files/test-[기본양식]-합포장용.xlsx"
    processed_file = etc_site_merge_packaging(excel_file_path)
    print("모든 처리가 완료되었습니다!")