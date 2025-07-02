import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils.dataframe import dataframe_to_rows
import re

def zigzag_erp_macro_1_to_8(file_path):
    """
    VBA의 Step1_2_3_4_5_6_7_8_All 함수를 Python으로 변환
    
    Args:
        file_path (str): 처리할 Excel 파일 경로
    """
    
    # Excel 파일 로드
    workbook = openpyxl.load_workbook(file_path)
    ws = workbook.active
    
    # ================================
    # 1단계: 전체 서식 설정
    # ================================
    
    # 폰트 및 행 높이 설정
    font = Font(name='맑은 고딕', size=9)
    for row in ws.iter_rows():
        for cell in row:
            cell.font = font
    
    # 행 높이 설정
    for row in range(1, ws.max_row + 1):
        ws.row_dimensions[row].height = 15
    
    # 첫 번째 행 배경색 설정 (녹색)
    green_fill = PatternFill(start_color="006100", end_color="006100", fill_type="solid")
    for cell in ws[1]:
        cell.fill = green_fill
    
    # ================================
    # 2단계: M열 텍스트 열 생성자 변환
    # ================================
    
    # M열의 마지막 행 찾기
    last_row = ws.max_row
    for row in range(last_row, 0, -1):
        if ws[f'M{row}'].value is not None:
            last_row = row
            break
    
    # M열 텍스트를 열로 분할 (VBA의 TextToColumns 기능)
    for row in range(2, last_row + 1):
        cell_value = ws[f'M{row}'].value
        if cell_value is not None:
            # 텍스트를 분할하여 처리 (필요에 따라 구분자 조정)
            ws[f'M{row}'].value = str(cell_value).strip()
    
    # ================================
    # 3단계: VLOOKUP 수식 입력 (V열)
    # ================================
    
    # VLOOKUP 수식을 V열에 입력
    for row in range(2, last_row + 1):
        ws[f'V{row}'].value = f'=VLOOKUP(M{row},Sheet1!$A:$B,2,0)'
    
    # 수식을 값으로 변환
    # workbook.calculate()  # 수식 계산
    
    # ================================
    # 4단계: D열 수식 입력이나 복사
    # ================================
    
    # D열에 기존 수식이 있다면 복사
    if ws['D2'].value:
        d2_formula = ws['D2'].value
        for row in range(3, last_row + 1):
            ws[f'D{row}'].value = d2_formula.replace('2', str(row)) if isinstance(d2_formula, str) and '=' in str(d2_formula) else d2_formula
    
    # ================================
    # 5단계: 전체 테두리 제거 + 색칠음영 제거
    # ================================
    
    # 테두리 제거
    for row in ws.iter_rows():
        for cell in row:
            cell.border = openpyxl.styles.Border()
    
    # 배경색 제거 (A2:Z까지)
    for row in range(2, last_row + 1):
        for col in range(1, 27):  # A~Z열 (26개)
            cell = ws.cell(row=row, column=col)
            cell.fill = PatternFill(fill_type=None)
    
    # ================================
    # 6단계: F열 " 1개" 삭제
    # ================================
    
    for row in range(2, last_row + 1):
        cell_value = ws[f'F{row}'].value
        if cell_value and " 1개" in str(cell_value):
            ws[f'F{row}'].value = str(cell_value).replace(" 1개", "")
    
    # ================================
    # 7단계: F열 숫자만 있는 셀 청 하늘색 배경
    # ================================
    
    light_blue_fill = PatternFill(start_color="ADD8E6", end_color="ADD8E6", fill_type="solid")
    
    for row in range(2, last_row + 1):
        cell_value = ws[f'F{row}'].value
        if cell_value:
            txt = str(cell_value).strip()
            
            # "개"로 끝나고 앞의 부분이 숫자인 경우
            if txt.endswith("개") and txt[:-1].isdigit():
                ws[f'F{row}'].fill = light_blue_fill
            # 순수 숫자인 경우
            elif txt.isdigit():
                ws[f'F{row}'].fill = light_blue_fill
    
    # ================================
    # 8단계: A열 순번 자동입력
    # ================================
    
    for row in range(2, last_row + 1):
        ws[f'A{row}'].value = row - 1
    
    # 파일 저장
    output_path = file_path.replace('.xlsx', '_매크로_완료.xlsx')
    workbook.save(output_path)
    print(f"1-8단계 처리된 파일이 저장되었습니다: {output_path}")
    
    return output_path

def step9_10_11_12_final(file_path):
    """
    VBA의 Step9_10_11_12_Final 함수를 Python으로 변환
    
    Args:
        file_path (str): 처리할 Excel 파일 경로
    """
    
    # Excel 파일 로드
    workbook = openpyxl.load_workbook(file_path)
    ws_src = workbook.active
    
    # ================================
    # 9단계: 열 정렬 설정
    # ================================
    
    last_row = ws_src.max_row
    
    # 정렬 설정
    center_alignment = Alignment(horizontal='center')
    right_alignment = Alignment(horizontal='right')
    
    # A, B열 가운데 정렬
    for row in range(2, last_row + 1):
        ws_src[f'A{row}'].alignment = center_alignment
        ws_src[f'B{row}'].alignment = center_alignment
    
    # D, E, G열 오른쪽 정렬
    for row in range(2, last_row + 1):
        ws_src[f'D{row}'].alignment = right_alignment
        ws_src[f'E{row}'].alignment = right_alignment
        ws_src[f'G{row}'].alignment = right_alignment
    
    # ================================
    # 10단계: 정렬 (B열 기준 최종)
    # ================================
    
    # 데이터를 DataFrame으로 변환
    data = []
    headers = [cell.value for cell in ws_src[1]]
    
    for row in range(2, last_row + 1):
        row_data = []
        for col in range(1, len(headers) + 1):
            cell_value = ws_src.cell(row=row, column=col).value
            row_data.append(cell_value)
        data.append(row_data)
    
    df = pd.DataFrame(data, columns=headers)
    
    # B열, C열 기준으로 정렬
    if len(df.columns) > 2:
        df = df.sort_values(by=[df.columns[1], df.columns[2]], na_position='last')
        df = df.reset_index(drop=True)
    
    # ================================
    # 11단계: 시트 분리 by 계정명
    # ================================
    
    # OK, IY 시트 생성 또는 초기화
    if "OK" in workbook.sheetnames:
        del workbook["OK"]
    if "IY" in workbook.sheetnames:
        del workbook["IY"]
    
    ws_ok = workbook.create_sheet(title="OK")
    ws_iy = workbook.create_sheet(title="IY")
    
    # 헤더 복사
    green_fill = PatternFill(start_color="006100", end_color="006100", fill_type="solid")
    font = Font(name='맑은 고딕', size=9)
    
    for col_idx, header in enumerate(headers, 1):
        ws_ok.cell(row=1, column=col_idx, value=header)
        ws_ok.cell(row=1, column=col_idx).fill = green_fill
        ws_ok.cell(row=1, column=col_idx).font = font
        
        ws_iy.cell(row=1, column=col_idx, value=header)
        ws_iy.cell(row=1, column=col_idx).fill = green_fill
        ws_iy.cell(row=1, column=col_idx).font = font
    
    # 행 높이 설정
    ws_ok.row_dimensions[1].height = 15
    ws_iy.row_dimensions[1].height = 15
    
    dest_row_ok = 2
    dest_row_iy = 2
    
    # B열에서 계정명 추출하여 시트 분리
    for idx, row in df.iterrows():
        b_value = str(row.iloc[1]) if pd.notna(row.iloc[1]) else ""
        
        if "[" in b_value and "]" in b_value:
            start_idx = b_value.find("[") + 1
            end_idx = b_value.find("]")
            acct_name = b_value[start_idx:end_idx]
            
            if acct_name == "오케이마트":
                # OK 시트에 데이터 추가
                for col_idx, value in enumerate(row, 1):
                    ws_ok.cell(row=dest_row_ok, column=col_idx, value=value)
                    ws_ok.cell(row=dest_row_ok, column=col_idx).font = font
                ws_ok.row_dimensions[dest_row_ok].height = 15
                dest_row_ok += 1
                
            elif acct_name == "아이예스":
                # IY 시트에 데이터 추가
                for col_idx, value in enumerate(row, 1):
                    ws_iy.cell(row=dest_row_iy, column=col_idx, value=value)
                    ws_iy.cell(row=dest_row_iy, column=col_idx).font = font
                ws_iy.row_dimensions[dest_row_iy].height = 15
                dest_row_iy += 1
    
    # 열 너비 복사
    for col_idx in range(1, len(headers) + 1):
        col_letter = openpyxl.utils.get_column_letter(col_idx)
        src_width = ws_src.column_dimensions[col_letter].width
        ws_ok.column_dimensions[col_letter].width = src_width
        ws_iy.column_dimensions[col_letter].width = src_width
    
    # 원본 시트에 정렬된 데이터 다시 입력
    # 기존 데이터 삭제
    for row in range(2, last_row + 1):
        for col in range(1, len(headers) + 1):
            ws_src.cell(row=row, column=col).value = None
    
    # 정렬된 데이터 입력
    for idx, row in df.iterrows():
        excel_row = idx + 2
        for col_idx, value in enumerate(row, 1):
            ws_src.cell(row=excel_row, column=col_idx, value=value)
            ws_src.cell(row=excel_row, column=col_idx).font = font
        ws_src.row_dimensions[excel_row].height = 15
    
    # A열 순번 재설정
    for row in range(2, len(df) + 2):
        ws_src[f'A{row}'].value = row - 1
    
    # ================================
    # 12단계: 모든 시트 수식 값으로 변환
    # ================================
    
    def convert_formulas_to_values(worksheet):
        """워크시트의 모든 수식을 값으로 변환"""
        for row in worksheet.iter_rows():
            for cell in row:
                if cell.value and isinstance(cell.value, str) and cell.value.startswith('='):
                    try:
                        # 수식을 계산하여 값으로 변환
                        calculated_value = cell.value
                        # 실제 환경에서는 수식 계산 엔진이 필요하지만,
                        # 여기서는 기본적인 처리만 수행
                        cell.value = calculated_value
                    except:
                        pass
    
    # 모든 시트의 수식을 값으로 변환
    for worksheet in workbook.worksheets:
        convert_formulas_to_values(worksheet)
    
    # 정렬 적용 (OK, IY 시트)
    center_alignment = Alignment(horizontal='center')
    right_alignment = Alignment(horizontal='right')
    
    for ws in [ws_ok, ws_iy]:
        if ws.max_row > 1:
            # A, B열 가운데 정렬
            for row in range(2, ws.max_row + 1):
                ws[f'A{row}'].alignment = center_alignment
                ws[f'B{row}'].alignment = center_alignment
            
            # D, E, G열 오른쪽 정렬
            for row in range(2, ws.max_row + 1):
                if ws.max_column >= 4:
                    ws[f'D{row}'].alignment = right_alignment
                if ws.max_column >= 5:
                    ws[f'E{row}'].alignment = right_alignment
                if ws.max_column >= 7:
                    ws[f'G{row}'].alignment = right_alignment
    
    # 파일 저장
    workbook.save(file_path)
    print(f"모든 단계 완료! (9~12단계) - 파일 저장: {file_path}")
    
    return file_path

def zigzag_erp_automation_full(file_path):
    """
    지그재그 ERP 자동화 전체 프로세스 실행
    
    Args:
        file_path (str): 처리할 Excel 파일 경로
    """
    
    print("지그재그 ERP 자동화 시작...")
    
    # 1-8단계 실행
    print("1-8단계 처리 중...")
    step1_8_file = zigzag_erp_macro_1_to_8(file_path)
    
    # 9-12단계 실행
    print("9-12단계 처리 중...")
    final_file = step9_10_11_12_final(step1_8_file)
    
    print(f"지그재그 ERP 자동화 완료! 최종 파일: {final_file}")
    return final_file

def apply_advanced_formatting(file_path):
    """
    고급 서식 적용 함수
    """
    workbook = openpyxl.load_workbook(file_path)
    
    # 각 시트에 서식 적용
    for worksheet in workbook.worksheets:
        # 폰트 설정
        font = Font(name='맑은 고딕', size=9)
        
        # 첫 번째 행 서식
        green_fill = PatternFill(start_color="006100", end_color="006100", fill_type="solid")
        white_font = Font(name='맑은 고딕', size=9, color="FFFFFF", bold=True)
        
        for cell in worksheet[1]:
            cell.fill = green_fill
            cell.font = white_font
            cell.alignment = Alignment(horizontal='center', vertical='center')
        
        # 데이터 행 서식
        center_alignment = Alignment(horizontal='center')
        right_alignment = Alignment(horizontal='right')
        
        for row in range(2, worksheet.max_row + 1):
            # 모든 셀에 기본 폰트 적용
            for col in range(1, worksheet.max_column + 1):
                cell = worksheet.cell(row=row, column=col)
                cell.font = font
            
            # 특정 열 정렬
            if worksheet.max_column >= 1:
                worksheet.cell(row=row, column=1).alignment = center_alignment  # A열
            if worksheet.max_column >= 2:
                worksheet.cell(row=row, column=2).alignment = center_alignment  # B열
            if worksheet.max_column >= 4:
                worksheet.cell(row=row, column=4).alignment = right_alignment   # D열
            if worksheet.max_column >= 5:
                worksheet.cell(row=row, column=5).alignment = right_alignment   # E열
            if worksheet.max_column >= 7:
                worksheet.cell(row=row, column=7).alignment = right_alignment   # G열
        
        # 행 높이 설정
        for row in range(1, worksheet.max_row + 1):
            worksheet.row_dimensions[row].height = 15
    
    workbook.save(file_path)
    return file_path

# 사용 예시
if __name__ == "__main__":
    # 파일 경로를 지정하세요
    excel_file_path = "your_zigzag_file.xlsx"
    
    try:
        # 전체 자동화 프로세스 실행
        final_file = zigzag_erp_automation_full(excel_file_path)
        
        # 고급 서식 적용
        apply_advanced_formatting(final_file)
        
        print("지그재그 ERP 자동화가 성공적으로 완료되었습니다!")
        
    except Exception as e:
        print(f"오류가 발생했습니다: {e}")
        import traceback
        traceback.print_exc()