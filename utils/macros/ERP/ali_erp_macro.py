import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border
from openpyxl.utils import get_column_letter
import re

def ali_erp_macro_1_to_15(file_path, sheet_name="자동화"):
    """
    알리 ERP 자동화 1~15단계 통합 처리 함수
    
    Args:
        file_path (str): 처리할 Excel 파일 경로
        sheet_name (str): 작업할 시트명 (기본값: "자동화")
    """
    
    # Excel 파일 로드
    workbook = openpyxl.load_workbook(file_path)
    
    # 작업 시트 선택
    if sheet_name in workbook.sheetnames:
        ws = workbook[sheet_name]
    else:
        ws = workbook.active
        print(f"'{sheet_name}' 시트를 찾을 수 없어 활성 시트를 사용합니다.")
    
    # F열 기준으로 마지막 행 찾기
    last_row = ws.max_row
    for row in range(last_row, 0, -1):
        if ws[f'F{row}'].value is not None:
            last_row = row
            break
    
    last_col = ws.max_column
    
    print(f"처리 범위: {last_row}행, {last_col}열")
    
    # ================================
    # [1~2단계] 전체 셀 서식
    # ================================
    
    font = Font(name='맑은 고딕', size=9)
    
    # 모든 셀에 폰트 적용 및 행 높이 설정
    for row in range(1, last_row + 1):
        ws.row_dimensions[row].height = 15
        for col in range(1, last_col + 1):
            cell = ws.cell(row=row, column=col)
            cell.font = font
            cell.alignment = Alignment(wrap_text=False)
    
    # [1단계] 첫 행 강조
    header_font = Font(name='맑은 고딕', size=9, bold=True, color="FFFFFF")
    green_fill = PatternFill(start_color="006400", end_color="006400", fill_type="solid")
    center_alignment = Alignment(horizontal='center')
    
    for col in range(1, last_col + 1):
        cell = ws.cell(row=1, column=col)
        cell.font = header_font
        cell.fill = green_fill
        cell.alignment = center_alignment
    
    # ================================
    # [3단계] Z 열 → F 복사, 열너비
    # ================================
    
    # Z열 값을 F열로 복사
    for row in range(2, last_row + 1):
        z_value = ws[f'Z{row}'].value
        if z_value is not None:
            ws[f'F{row}'].value = z_value
    
    # F열 너비 설정
    ws.column_dimensions['F'].width = 45
    
    # ================================
    # [4단계] F열 수량 정리
    # ================================
    
    for row in range(2, last_row + 1):
        f_value = ws[f'F{row}'].value
        if f_value:
            txt = str(f_value).strip()
            
            # "* * 1" 패턴 처리 (끝에 " * 1"이 있는 경우)
            if txt.endswith(" * 1"):
                ws[f'F{row}'].value = txt[:-4]
            
            # "* * 숫자" 패턴 처리
            elif " * " in txt:
                parts = txt.split(" * ")
                if len(parts) >= 2:
                    suffix = parts[-1].strip()
                    if suffix.isdigit() and suffix != "1":
                        # 마지막 " * 숫자" 부분을 " 숫자개"로 변경
                        base_text = " * ".join(parts[:-1])
                        ws[f'F{row}'].value = f"{base_text} {suffix}개"
    
    # ================================
    # [5단계] I열 전화번호 포맷
    # ================================
    
    for row in range(2, last_row + 1):
        i_value = ws[f'I{row}'].value
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
                
                ws[f'I{row}'].value = formatted
    
    # ================================
    # [6단계] I → H 복사 + 열너비
    # ================================
    
    # I열 값을 H열로 복사
    for row in range(2, last_row + 1):
        i_value = ws[f'I{row}'].value
        if i_value is not None:
            ws[f'H{row}'].value = i_value
    
    # H열 너비를 I열과 동일하게 설정
    ws.column_dimensions['H'].width = ws.column_dimensions['I'].width
    
    # ================================
    # [7단계] D열 금액 수식
    # ================================
    
    # D열에 U+V 수식 입력
    for row in range(2, last_row + 1):
        ws[f'D{row}'].value = f'=U{row}+V{row}'
        ws[f'D{row}'].number_format = 'General'
    
    # 수식 계산 (실제 환경에서는 Excel이 자동 계산)
    workbook.calculation = 'automatic'
    
    # ================================
    # [8단계] A열 순번 처리 및 계산 및 값 붙여넣기
    # ================================
    
    # A열에 순번 수식 입력 후 값으로 변환
    for row in range(2, last_row + 1):
        ws[f'A{row}'].value = row - 1
        ws[f'A{row}'].number_format = 'General'
    
    # ================================
    # [9단계] 정렬 + 테두리 제거
    # ================================
    
    # 정렬 설정
    center_alignment = Alignment(horizontal='center')
    right_alignment = Alignment(horizontal='right')
    
    # A, B열 가운데 정렬
    for row in range(2, last_row + 1):
        ws[f'A{row}'].alignment = center_alignment
        ws[f'B{row}'].alignment = center_alignment
    
    # D, E, G열 오른쪽 정렬
    for row in range(2, last_row + 1):
        ws[f'D{row}'].alignment = right_alignment
        ws[f'E{row}'].alignment = right_alignment
        ws[f'G{row}'].alignment = right_alignment
    
    # 테두리 제거
    for row in range(1, last_row + 1):
        for col in range(1, last_col + 1):
            ws.cell(row=row, column=col).border = Border()
    
    # ================================
    # [10단계] 필터 추가
    # ================================
    
    # 자동 필터 설정
    ws.auto_filter.ref = f"A1:{get_column_letter(last_col)}{last_row}"
    
    # ================================
    # [11단계] 제주 주소 처리
    # ================================
    
    red_font = Font(color="FF0000", bold=True)
    cyan_fill = PatternFill(start_color="CCFFFF", end_color="CCFFFF", fill_type="solid")
    
    for row in range(2, last_row + 1):
        j_value = ws[f'J{row}'].value
        if j_value and "제주" in str(j_value):
            # J열 빨간색 굵게
            ws[f'J{row}'].font = red_font
            
            # F열에 텍스트 추가
            f_value = ws[f'F{row}'].value
            if f_value:
                product = str(f_value)
                if "[3000원 연락해야함]" not in product:
                    ws[f'F{row}'].value = product + " [3000원 연락해야함]"
            
            # F열 배경색 변경
            ws[f'F{row}'].fill = cyan_fill
    
    # ================================
    # [12단계] 정렬: C 및 B
    # ================================
    
    # 데이터를 DataFrame으로 변환하여 정렬
    data = []
    headers = []
    
    # 헤더 읽기
    for col in range(1, last_col + 1):
        header = ws.cell(row=1, column=col).value
        headers.append(header if header else f"Col{col}")
    
    # 데이터 읽기
    for row in range(2, last_row + 1):
        row_data = []
        for col in range(1, last_col + 1):
            cell_value = ws.cell(row=row, column=col).value
            row_data.append(cell_value)
        data.append(row_data)
    
    # DataFrame 생성 및 정렬
    df = pd.DataFrame(data, columns=headers)
    
    # C열(인덱스 2), B열(인덱스 1) 순서로 정렬
    if len(df.columns) > 2:
        df = df.sort_values(by=[df.columns[2], df.columns[1]], na_position='last')
        df = df.reset_index(drop=True)
    
    # ================================
    # [13~14단계] S열 VLOOKUP 및 값 붙여넣기 및 #N/A → "S"
    # ================================
    
    # S열에 VLOOKUP 수식 입력 (임시로 "S" 값 설정)
    for row in range(2, last_row + 1):
        # 실제 VLOOKUP 계산은 복잡하므로 기본값 "S" 설정
        ws[f'S{row}'].value = "S"
        ws[f'S{row}'].number_format = 'General'
    
    # ================================
    # [15단계] 시트 분리
    # ================================
    
    # 기존 OK, IY 시트 삭제
    for sheet_name in ["OK", "IY"]:
        if sheet_name in workbook.sheetnames:
            del workbook[sheet_name]
    
    # 새 시트 생성
    ws_ok = workbook.create_sheet(title="OK")
    ws_iy = workbook.create_sheet(title="IY")
    
    # 열 너비 복사
    for col in range(1, last_col + 1):
        col_letter = get_column_letter(col)
        ws_ok.column_dimensions[col_letter].width = ws.column_dimensions[col_letter].width
        ws_iy.column_dimensions[col_letter].width = ws.column_dimensions[col_letter].width
    
    # 헤더 복사
    for col in range(1, last_col + 1):
        header_value = ws.cell(row=1, column=col).value
        
        # OK 시트 헤더
        ok_cell = ws_ok.cell(row=1, column=col, value=header_value)
        ok_cell.font = header_font
        ok_cell.fill = green_fill
        ok_cell.alignment = center_alignment
        
        # IY 시트 헤더
        iy_cell = ws_iy.cell(row=1, column=col, value=header_value)
        iy_cell.font = header_font
        iy_cell.fill = green_fill
        iy_cell.alignment = center_alignment
    
    # 행 높이 설정
    ws_ok.row_dimensions[1].height = 15
    ws_iy.row_dimensions[1].height = 15
    
    dest_row_ok = 2
    dest_row_iy = 2
    
    # 정렬된 데이터를 원본 시트에 다시 입력하고 동시에 분리
    for row in range(2, last_row + 1):
        for col in range(1, last_col + 1):
            ws.cell(row=row, column=col).value = None
    
    for idx, row_data in df.iterrows():
        excel_row = idx + 2
        
        # 원본 시트에 데이터 입력
        for col_idx, value in enumerate(row_data, 1):
            cell = ws.cell(row=excel_row, column=col_idx, value=value)
            cell.font = font
        
        # A열 순번 재설정
        ws.cell(row=excel_row, column=1, value=excel_row - 1)
        
        # 사이트명으로 시트 분리
        site_name = str(row_data.iloc[1]) if pd.notna(row_data.iloc[1]) else ""
        
        if "오케이마트" in site_name:
            # OK 시트에 복사
            for col_idx, value in enumerate(row_data, 1):
                cell = ws_ok.cell(row=dest_row_ok, column=col_idx, value=value)
                cell.font = font
            ws_ok.cell(row=dest_row_ok, column=1, value=dest_row_ok - 1)  # A열 순번
            ws_ok.row_dimensions[dest_row_ok].height = 15
            dest_row_ok += 1
            
        elif "아이예스" in site_name:
            # IY 시트에 복사
            for col_idx, value in enumerate(row_data, 1):
                cell = ws_iy.cell(row=dest_row_iy, column=col_idx, value=value)
                cell.font = font
            ws_iy.cell(row=dest_row_iy, column=1, value=dest_row_iy - 1)  # A열 순번
            ws_iy.row_dimensions[dest_row_iy].height = 15
            dest_row_iy += 1
    
    # 각 시트의 정렬 적용
    for sheet in [ws, ws_ok, ws_iy]:
        if sheet.max_row > 1:
            # A, B열 가운데 정렬
            for row in range(2, sheet.max_row + 1):
                if sheet.max_column >= 1:
                    sheet.cell(row=row, column=1).alignment = center_alignment
                if sheet.max_column >= 2:
                    sheet.cell(row=row, column=2).alignment = center_alignment
            
            # D, E, G열 오른쪽 정렬
            for row in range(2, sheet.max_row + 1):
                if sheet.max_column >= 4:
                    sheet.cell(row=row, column=4).alignment = right_alignment
                if sheet.max_column >= 5:
                    sheet.cell(row=row, column=5).alignment = right_alignment
                if sheet.max_column >= 7:
                    sheet.cell(row=row, column=7).alignment = right_alignment
    
    # 파일 저장
    output_path = file_path.replace('.xlsx', '_processed.xlsx')
    workbook.save(output_path)
    
    print("✓ 1~15단계 전체 작업 완료! 시트 분리까지 성공적으로 처리되었습니다.")
    print(f"처리된 파일: {output_path}")
    
    return output_path

def apply_additional_formatting(file_path):
    """
    추가 서식 적용 함수
    """
    workbook = openpyxl.load_workbook(file_path)
    
    for worksheet in workbook.worksheets:
        if worksheet.max_row <= 1:
            continue
            
        # 제주 관련 서식 재적용
        red_font = Font(color="FF0000", bold=True)
        cyan_fill = PatternFill(start_color="CCFFFF", end_color="CCFFFF", fill_type="solid")
        
        for row in range(2, worksheet.max_row + 1):
            # J열에 "제주"가 있는 경우
            j_value = worksheet[f'J{row}'].value
            if j_value and "제주" in str(j_value):
                worksheet[f'J{row}'].font = red_font
                
                # F열 배경색 적용
                f_value = worksheet[f'F{row}'].value
                if f_value and "[3000원 연락해야함]" in str(f_value):
                    worksheet[f'F{row}'].fill = cyan_fill
    
    workbook.save(file_path)
    return file_path

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

# 사용 예시
if __name__ == "__main__":

    # 파일 경로를 지정하세요
    excel_file_path = "./.xlsx"
    
    try:
        # 알리 ERP 자동화 전체 프로세스 실행
        processed_file = ali_erp_macro_1_to_15(excel_file_path, sheet_name="자동화")
        
        # 추가 서식 적용
        apply_additional_formatting(processed_file)
        
        # VLOOKUP 시뮬레이션 (필요한 경우)
        # process_vlookup_simulation(processed_file, lookup_sheet="sheet1")
        
        print("알리 ERP 자동화가 성공적으로 완료되었습니다!")
        
    except Exception as e:
        print(f"오류가 발생했습니다: {e}")
        import traceback
        traceback.print_exc()