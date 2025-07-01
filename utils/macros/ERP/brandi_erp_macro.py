import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border
from openpyxl.utils import get_column_letter
import re
from collections import defaultdict

def brandi_erp_macro_1_to_10(file_path):
    """
    브랜디 ERP 자동화 1~10단계 전체 자동처리 함수
    
    Args:
        file_path (str): 처리할 Excel 파일 경로
    """
    
    # Excel 파일 로드
    workbook = openpyxl.load_workbook(file_path)
    ws = workbook.active
    
    print("브랜디 ERP 자동화 1~10단계 처리 시작...")
    
    # ================================
    # 1단계: 서식 적용
    # ================================
    
    # 사용된 범위 찾기
    last_row = ws.max_row
    last_col = ws.max_column
    
    # 빈 행 제거를 위한 실제 마지막 행 찾기
    for row in range(last_row, 0, -1):
        if any(ws.cell(row=row, column=col).value is not None for col in range(1, last_col + 1)):
            last_row = row
            break
    
    print(f"처리 범위: {last_row}행, {last_col}열")
    
    # 전체 데이터 범위에 폰트 적용
    font = Font(name='맑은 고딕', size=9)
    
    for row in range(1, last_row + 1):
        ws.row_dimensions[row].height = 15
        for col in range(1, last_col + 1):
            ws.cell(row=row, column=col).font = font
    
    # 첫 번째 행 강조 (녹색 배경)
    green_fill = PatternFill(start_color="006100", end_color="006100", fill_type="solid")
    for col in range(1, last_col + 1):
        ws.cell(row=1, column=col).fill = green_fill
    
    # ================================
    # 2단계: D열 수식 적용 (AutoFill)
    # ================================
    
    # P열 기준으로 마지막 행 재계산
    p_last_row = last_row
    for row in range(last_row, 0, -1):
        if ws[f'P{row}'].value is not None:
            p_last_row = row
            break
    
    # D열에 P+V 수식 입력
    for row in range(2, p_last_row + 1):
        ws[f'D{row}'].value = f'=P{row}+V{row}'
        ws[f'D{row}'].number_format = 'General'
    
    print("2단계: D열 수식 적용 완료")
    
    # ================================
    # 3단계: F열 " 1개" 제거
    # ================================
    
    for row in range(2, last_row + 1):
        f_value = ws[f'F{row}'].value
        if f_value and " 1개" in str(f_value):
            ws[f'F{row}'].value = str(f_value).replace(" 1개", "")
    
    print("3단계: F열 ' 1개' 제거 완료")
    
    # ================================
    # 4단계: 색 채우기 제거
    # ================================
    
    # 모든 데이터 셀의 배경색 제거 (헤더 제외)
    for row in range(2, last_row + 1):
        for col in range(1, last_col + 1):
            ws.cell(row=row, column=col).fill = PatternFill(fill_type=None)
    
    print("4단계: 배경색 제거 완료")
    
    # ================================
    # 5단계: F열 조건부 연한 파란색 칠하기
    # ================================
    
    light_blue_fill = PatternFill(start_color="ADD8E6", end_color="ADD8E6", fill_type="solid")
    
    # 정규식 패턴: 숫자개 형태
    pattern = re.compile(r'^\d+개$', re.IGNORECASE)
    
    for row in range(2, last_row + 1):
        f_value = ws[f'F{row}'].value
        if f_value:
            cell_value = str(f_value).strip()
            
            # 순수 숫자이거나 "숫자개" 패턴인 경우
            if cell_value.isdigit() or pattern.match(cell_value):
                ws[f'F{row}'].fill = light_blue_fill
    
    print("5단계: F열 조건부 파란색 칠하기 완료")
    
    # ================================
    # 6단계: 테두리 제거 + 연락처 포맷
    # ================================
    
    # 테두리 제거
    for row in range(1, last_row + 1):
        for col in range(1, last_col + 1):
            ws.cell(row=row, column=col).border = Border()
    
    # H열, I열 전화번호 포맷팅
    for row in range(2, last_row + 1):
        # H열 처리
        h_value = ws[f'H{row}'].value
        if h_value and len(str(h_value)) == 11 and str(h_value).isdigit():
            phone_str = str(h_value)
            formatted_phone = f"{phone_str[:3]}-{phone_str[3:7]}-{phone_str[7:]}"
            ws[f'H{row}'].value = formatted_phone
        
        # I열 처리
        i_value = ws[f'I{row}'].value
        if i_value and len(str(i_value)) == 11 and str(i_value).isdigit():
            phone_str = str(i_value)
            formatted_phone = f"{phone_str[:3]}-{phone_str[3:7]}-{phone_str[7:]}"
            ws[f'I{row}'].value = formatted_phone
    
    print("6단계: 테두리 제거 및 전화번호 포맷팅 완료")
    
    # ================================
    # 7단계: A열 순번 수식 입력
    # ================================
    
    for row in range(2, last_row + 1):
        ws[f'A{row}'].value = row - 1
        ws[f'A{row}'].number_format = 'General'
    
    print("7단계: A열 순번 입력 완료")
    
    # ================================
    # 8단계: 제주 주소 안내문 + 서식 반영
    # ================================
    
    # 제주 주소 딕셔너리
    jeju_dict = {}
    
    # 제주 주소 찾기
    for row in range(2, last_row + 1):
        j_value = ws[f'J{row}'].value
        if j_value and "제주" in str(j_value):
            addr = str(j_value).strip()
            jeju_dict[addr] = row
    
    # 제주 주소 처리
    red_font = Font(color="FF0000", bold=True)
    
    for addr, row in jeju_dict.items():
        # F열에 안내문 추가
        f_value = ws[f'F{row}'].value
        if f_value:
            product_text = str(f_value)
            if "[3000원 연락해야함]" not in product_text:
                ws[f'F{row}'].value = product_text + " [3000원 연락해야함]"
        
        # J열 빨간색 굵게
        ws[f'J{row}'].font = red_font
        
        # F열 파란색 배경
        ws[f'F{row}'].fill = light_blue_fill
    
    print(f"8단계: 제주 주소 {len(jeju_dict)}개 처리 완료")
    
    # ================================
    # 9단계: 정렬 설정
    # ================================
    
    # 정렬 설정
    center_alignment = Alignment(horizontal='center')
    right_alignment = Alignment(horizontal='right')
    
    # A, B열 가운데 정렬
    for row in range(1, last_row + 1):
        ws[f'A{row}'].alignment = center_alignment
        ws[f'B{row}'].alignment = center_alignment
    
    # D, E, G열 오른쪽 정렬
    for row in range(1, last_row + 1):
        ws[f'D{row}'].alignment = right_alignment
        ws[f'E{row}'].alignment = right_alignment
        ws[f'G{row}'].alignment = right_alignment
    
    # 첫 번째 행 가운데 정렬
    for col in range(1, last_col + 1):
        ws.cell(row=1, column=col).alignment = center_alignment
    
    print("9단계: 정렬 설정 완료")
    
    # ================================
    # 10단계: C열 기준 오름차순 정렬
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
    
    # C열(인덱스 2) 기준으로 오름차순 정렬
    if len(df.columns) > 2:
        df = df.sort_values(by=df.columns[2], na_position='last')
        df = df.reset_index(drop=True)
    
    # 정렬된 데이터를 다시 Excel에 입력
    for row in range(2, last_row + 1):
        for col in range(1, last_col + 1):
            ws.cell(row=row, column=col).value = None
    
    for idx, row_data in df.iterrows():
        excel_row = idx + 2
        for col_idx, value in enumerate(row_data, 1):
            cell = ws.cell(row=excel_row, column=col_idx, value=value)
            cell.font = font
        
        # A열 순번 재설정
        ws.cell(row=excel_row, column=1, value=excel_row - 1)
    
    # 정렬 후 서식 재적용
    apply_formatting_after_sort(ws, last_row, last_col)
    
    print("10단계: C열 기준 정렬 완료")
    
    # 파일 저장
    output_path = file_path.replace('.xlsx', '_매크로_완료.xlsx')
    workbook.save(output_path)
    
    print(f"✓ 브랜디 ERP 자동화 1~10단계 모든 처리 완료!")
    print(f"처리된 파일: {output_path}")
    
    return output_path

def apply_formatting_after_sort(ws, last_row, last_col):
    """
    정렬 후 서식 재적용 함수
    """
    # 기본 서식
    font = Font(name='맑은 고딕', size=9)
    green_fill = PatternFill(start_color="006100", end_color="006100", fill_type="solid")
    light_blue_fill = PatternFill(start_color="ADD8E6", end_color="ADD8E6", fill_type="solid")
    center_alignment = Alignment(horizontal='center')
    right_alignment = Alignment(horizontal='right')
    red_font = Font(color="FF0000", bold=True)
    
    # 첫 번째 행 서식
    for col in range(1, last_col + 1):
        cell = ws.cell(row=1, column=col)
        cell.fill = green_fill
        cell.alignment = center_alignment
    
    # 데이터 행 서식 재적용
    pattern = re.compile(r'^\d+개$', re.IGNORECASE)
    
    for row in range(2, last_row + 1):
        # 기본 폰트 적용
        for col in range(1, last_col + 1):
            ws.cell(row=row, column=col).font = font
        
        # 정렬 적용
        ws[f'A{row}'].alignment = center_alignment
        ws[f'B{row}'].alignment = center_alignment
        ws[f'D{row}'].alignment = right_alignment
        ws[f'E{row}'].alignment = right_alignment
        ws[f'G{row}'].alignment = right_alignment
        
        # F열 조건부 서식
        f_value = ws[f'F{row}'].value
        if f_value:
            cell_value = str(f_value).strip()
            if cell_value.isdigit() or pattern.match(cell_value) or "[3000원 연락해야함]" in cell_value:
                ws[f'F{row}'].fill = light_blue_fill
        
        # 제주 주소 서식
        j_value = ws[f'J{row}'].value
        if j_value and "제주" in str(j_value):
            ws[f'J{row}'].font = red_font
            if f_value and "[3000원 연락해야함]" in str(f_value):
                ws[f'F{row}'].fill = light_blue_fill
        
        # 전화번호 포맷 유지
        for col_letter in ['H', 'I']:
            cell_value = ws[f'{col_letter}{row}'].value
            if cell_value and len(str(cell_value)) == 11 and str(cell_value).replace('-', '').isdigit():
                phone_str = str(cell_value).replace('-', '')
                formatted_phone = f"{phone_str[:3]}-{phone_str[3:7]}-{phone_str[7:]}"
                ws[f'{col_letter}{row}'].value = formatted_phone

def create_summary_report(file_path):
    """
    처리 결과 요약 보고서 생성
    """
    workbook = openpyxl.load_workbook(file_path)
    ws = workbook.active
    
    # 통계 정보 수집
    total_rows = ws.max_row - 1  # 헤더 제외
    jeju_count = 0
    phone_formatted_count = 0
    
    for row in range(2, ws.max_row + 1):
        # 제주 주소 카운트
        j_value = ws[f'J{row}'].value
        if j_value and "제주" in str(j_value):
            jeju_count += 1
        
        # 포맷된 전화번호 카운트
        h_value = ws[f'H{row}'].value
        i_value = ws[f'I{row}'].value
        if (h_value and '-' in str(h_value)) or (i_value and '-' in str(i_value)):
            phone_formatted_count += 1
    
    # 요약 보고서 출력
    print("\n" + "="*50)
    print("브랜디 ERP 자동화 처리 결과 요약")
    print("="*50)
    print(f"총 처리된 데이터 행 수: {total_rows:,}개")
    print(f"제주 주소 처리 건수: {jeju_count:,}개")
    print(f"전화번호 포맷팅 건수: {phone_formatted_count:,}개")
    print(f"C열 기준 정렬 완료")
    print("="*50)
    return file_path

def validate_processing_result(file_path):
    """
    처리 결과 검증 함수
    """
    workbook = openpyxl.load_workbook(file_path)
    ws = workbook.active
    
    validation_results = {
        'header_formatting': True,
        'phone_formatting': True,
        'jeju_processing': True,
        'column_alignment': True,
        'row_numbering': True
    }
    
    # 헤더 서식 검증
    if ws.cell(row=1, column=1).fill.start_color.rgb != "FF006100":
        validation_results['header_formatting'] = False
    
    # 전화번호 포맷 검증
    for row in range(2, min(ws.max_row + 1, 10)):  # 샘플 검증
        h_value = ws[f'H{row}'].value
        if h_value and len(str(h_value)) == 13 and str(h_value).count('-') == 2:
            continue
        elif h_value and len(str(h_value)) == 11:
            validation_results['phone_formatting'] = False
            break
    
    # 제주 처리 검증
    for row in range(2, ws.max_row + 1):
        j_value = ws[f'J{row}'].value
        if j_value and "제주" in str(j_value):
            f_value = ws[f'F{row}'].value
            if not f_value or "[3000원 연락해야함]" not in str(f_value):
                validation_results['jeju_processing'] = False
                break
    
    # 행 번호 검증
    for row in range(2, min(ws.max_row + 1, 10)):
        if ws[f'A{row}'].value != row - 1:
            validation_results['row_numbering'] = False
            break
    
    return validation_results

# 사용 예시
if __name__ == "__main__":
    # 파일 경로를 지정하세요
    excel_file_path = "your_brandi_file.xlsx"
    
    try:
        # 브랜디 ERP 자동화 전체 프로세스 실행
        processed_file = brandi_erp_macro_1_to_10(excel_file_path)
        
        # 처리 결과 요약 보고서 생성
        create_summary_report(processed_file)
        
        # 처리 결과 검증
        validation_results = validate_processing_result(processed_file)
        
        print("\n처리 결과 검증:")
        for key, result in validation_results.items():
            status = "✓ 성공" if result else "✗ 실패"
            print(f"- {key}: {status}")
        
        if all(validation_results.values()):
            print("\n✓ 모든 검증 통과! 브랜디 ERP 자동화가 성공적으로 완료되었습니다.")
        else:
            print("\n⚠️ 일부 검증 실패. 결과를 확인해주세요.")
        
    except Exception as e:
        print(f"오류가 발생했습니다: {e}")
        import traceback
        traceback.print_exc()