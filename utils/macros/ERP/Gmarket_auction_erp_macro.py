import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border
from openpyxl.utils import get_column_letter
import re
from collections import defaultdict

def gmarket_auction_erp_1_to_8(file_path):
    """
    G,옥 ERP 자동화 1~8단계 실행 함수
    
    Args:
        file_path (str): 처리할 Excel 파일 경로
    """
    
    # Excel 파일 로드
    workbook = openpyxl.load_workbook(file_path)
    ws = workbook.worksheets[0]  # 첫 번째 시트
    
    print("G,옥 ERP 자동화 1~8단계 처리 시작...")
    
    # ================================
    # [1단계] 폰트 및 행 너비 설정
    # ================================
    
    font = Font(name='맑은 고딕', size=9)
    
    # 모든 셀에 폰트 적용
    for row in ws.iter_rows():
        for cell in row:
            cell.font = font
    
    # 모든 행 높이 15로 설정
    for row in range(1, ws.max_row + 1):
        ws.row_dimensions[row].height = 15
    
    print("1단계: 폰트 및 행 높이 설정 완료")
    
    # ================================
    # [2단계] D열 수식 활성화 및 채우기
    # ================================
    
    # D열 전체 숫자 포맷
    for row in range(1, ws.max_row + 1):
        ws[f'D{row}'].number_format = 'General'
    
    # B열 기준으로 마지막 행 찾기
    last_row = ws.max_row
    for row in range(last_row, 0, -1):
        if ws[f'B{row}'].value is not None:
            last_row = row
            break
    
    # D2 수식을 다른 행으로 복사 (기존 수식이 있다고 가정)
    if ws['D2'].value and isinstance(ws['D2'].value, str) and ws['D2'].value.startswith('='):
        d2_formula = ws['D2'].value
        for row in range(3, last_row + 1):
            # 수식에서 행 번호 치환
            new_formula = d2_formula.replace('2', str(row)) if '2' in d2_formula else d2_formula
            ws[f'D{row}'].value = new_formula
    
    print("2단계: D열 수식 처리 완료")
    
    # ================================
    # [3단계] 바구니 중복 제거
    # ================================
    
    basket_dict = {}
    
    # Q열 기준으로 마지막 행 찾기
    q_last_row = last_row
    for row in range(last_row, 0, -1):
        if ws[f'Q{row}'].value is not None:
            q_last_row = row
            break
    
    # 첫 번째 패스: 바구니 번호별로 배송비가 있는 첫 번째 행 기록
    for row in range(2, q_last_row + 1):
        basket_no = str(ws[f'Q{row}'].value).strip() if ws[f'Q{row}'].value else ""
        shipping_cost = ws[f'V{row}'].value
        
        if basket_no and basket_no != "":
            if basket_no not in basket_dict:
                # 배송비가 0이 아니고 비어있지 않은 경우만 기록
                if shipping_cost and shipping_cost != 0:
                    basket_dict[basket_no] = row
    
    # 두 번째 패스: 중복 바구니의 배송비를 0으로 설정
    for row in range(2, q_last_row + 1):
        basket_no = str(ws[f'Q{row}'].value).strip() if ws[f'Q{row}'].value else ""
        
        if basket_no and basket_no != "":
            if basket_no in basket_dict:
                # 첫 번째 발생 행이 아닌 경우 배송비를 0으로 설정
                if basket_dict[basket_no] != row:
                    ws[f'V{row}'].value = 0
    
    print(f"3단계: {len(basket_dict)}개 바구니 중복 제거 완료")
    
    # ================================
    # [4단계] A열 순번 수식 + 색칠음영 제거
    # ================================
    
    # A열 숫자 포맷
    for row in range(1, ws.max_row + 1):
        ws[f'A{row}'].number_format = 'General'
    
    # A열에 순번 입력
    for row in range(2, last_row + 1):
        ws[f'A{row}'].value = row - 1
    
    # 색칠 음영 제거 (A2:Z까지)
    for row in range(2, last_row + 1):
        for col in range(1, 27):  # A~Z열
            cell = ws.cell(row=row, column=col)
            cell.fill = PatternFill(fill_type=None)
    
    print("4단계: A열 순번 입력 및 배경색 제거 완료")
    
    # ================================
    # [5단계] 정렬 및 E열 숫자 변환
    # ================================
    
    # 정렬 설정
    center_alignment = Alignment(horizontal='center')
    right_alignment = Alignment(horizontal='right')
    
    # A, B열 가운데 정렬
    for row in range(1, last_row + 1):
        ws[f'A{row}'].alignment = center_alignment
        ws[f'B{row}'].alignment = center_alignment
    
    # D, G열 오른쪽 정렬
    for row in range(1, last_row + 1):
        ws[f'D{row}'].alignment = right_alignment
        ws[f'G{row}'].alignment = right_alignment
    
    # E열 숫자 변환 및 오른쪽 정렬
    e_last_row = last_row
    for row in range(last_row, 0, -1):
        if ws[f'E{row}'].value is not None:
            e_last_row = row
            break
    
    for row in range(2, e_last_row + 1):
        e_value = ws[f'E{row}'].value
        if e_value and str(e_value).replace('.', '').replace('-', '').isdigit():
            ws[f'E{row}'].value = float(e_value) if '.' in str(e_value) else int(float(e_value))
        ws[f'E{row}'].alignment = right_alignment
    
    print("5단계: 정렬 및 E열 숫자 변환 완료")
    
    # ================================
    # [6단계] F열에서 " 1개" 제거
    # ================================
    
    f_last_row = last_row
    for row in range(last_row, 0, -1):
        if ws[f'F{row}'].value is not None:
            f_last_row = row
            break
    
    for row in range(2, f_last_row + 1):
        f_value = ws[f'F{row}'].value
        if f_value and str(f_value).endswith(" 1개"):
            ws[f'F{row}'].value = str(f_value)[:-3]  # 마지막 3글자 제거
    
    print("6단계: F열 ' 1개' 제거 완료")
    
    # ================================
    # [7단계] F열 모르겠는 셀 색칠음영 (하늘색)
    # ================================
    
    light_blue_fill = PatternFill(start_color="ADD8E6", end_color="ADD8E6", fill_type="solid")
    
    for row in range(2, f_last_row + 1):
        f_value = ws[f'F{row}'].value
        cell_value = str(f_value).strip() if f_value else ""
        
        # 조건: 빈 셀, 모든 문자가 #인 경우, 숫자+개 형태
        should_highlight = False
        
        # 빈 셀
        if cell_value == "" or cell_value == "None":
            should_highlight = True
        
        # 모든 문자가 #인 경우
        elif cell_value and all(c == '#' for c in cell_value):
            should_highlight = True
        
        # "숫자개" 형태인 경우
        elif cell_value.endswith("개"):
            number_part = cell_value[:-1]
            if number_part.isdigit():
                should_highlight = True
        
        if should_highlight:
            ws[f'F{row}'].fill = light_blue_fill
    
    print("7단계: F열 조건부 하이라이트 완료")
    
    # ================================
    # [8단계] 1행 가운데 정렬 + 진한 초록색 배경
    # ================================
    
    # 첫 번째 행 서식
    dark_green_fill = PatternFill(start_color="008000", end_color="008000", fill_type="solid")
    white_font = Font(name='맑은 고딕', size=9, color="FFFFFF", bold=True)
    
    for col in range(1, ws.max_column + 1):
        cell = ws.cell(row=1, column=col)
        cell.alignment = center_alignment
        cell.fill = dark_green_fill
        cell.font = white_font
    
    print("8단계: 헤더 서식 완료")
    
    # 파일 저장
    output_path = file_path.replace('.xlsx', '_매크로_완료.xlsx')
    workbook.save(output_path)
    print(f"1~8단계 처리 완료! 파일 저장: {output_path}")
    
    return output_path

def run_steps_9_to_11(file_path):
    """
    G,옥 ERP 자동화 9~11단계 실행 함수
    
    Args:
        file_path (str): 처리할 Excel 파일 경로
    """
    
    # Excel 파일 로드
    workbook = openpyxl.load_workbook(file_path)
    ws_source = workbook.worksheets[0]  # 첫 번째 시트
    
    print("G,옥 ERP 자동화 9~11단계 처리 시작...")
    
    # ================================
    # [9-1] 전체 테두리 제거
    # ================================
    
    for row in ws_source.iter_rows():
        for cell in row:
            cell.border = Border()
    
    print("9-1단계: 테두리 제거 완료")
    
    # ================================
    # [9-2, 9-3] C열 정렬 → B열 정렬
    # ================================
    
    # 마지막 행 찾기
    last_row = ws_source.max_row
    for row in range(last_row, 0, -1):
        if any(ws_source.cell(row=row, column=col).value is not None for col in range(1, ws_source.max_column + 1)):
            last_row = row
            break
    
    # 데이터를 DataFrame으로 변환
    data = []
    headers = []
    
    # 헤더 읽기
    for col in range(1, ws_source.max_column + 1):
        header = ws_source.cell(row=1, column=col).value
        headers.append(header if header else f"Col{col}")
    
    # 데이터 읽기
    for row in range(2, last_row + 1):
        row_data = []
        for col in range(1, ws_source.max_column + 1):
            cell_value = ws_source.cell(row=row, column=col).value
            row_data.append(cell_value)
        data.append(row_data)
    
    # DataFrame 생성 및 정렬
    df = pd.DataFrame(data, columns=headers)
    
    # C열(인덱스 2), B열(인덱스 1) 순서로 정렬
    if len(df.columns) > 2:
        df = df.sort_values(by=[df.columns[2], df.columns[1]], na_position='last')
        df = df.reset_index(drop=True)
    
    print("9-2, 9-3단계: C열, B열 순서 정렬 완료")
    
    # ================================
    # [10-1] 시트 분리 준비
    # ================================
    
    # 기존 시트 삭제
    sheets_to_delete = ["OK,CL,BB", "IY"]
    for sheet_name in sheets_to_delete:
        if sheet_name in workbook.sheetnames:
            del workbook[sheet_name]
    
    # 새 시트 생성
    ws_ok = workbook.create_sheet(title="OK,CL,BB")
    ws_iy = workbook.create_sheet(title="IY")
    
    # 헤더 복사
    dark_green_fill = PatternFill(start_color="008000", end_color="008000", fill_type="solid")
    white_font = Font(name='맑은 고딕', size=9, color="FFFFFF", bold=True)
    center_alignment = Alignment(horizontal='center')
    
    for col in range(1, len(headers) + 1):
        header_value = headers[col-1]
        
        # OK 시트 헤더
        ok_cell = ws_ok.cell(row=1, column=col, value=header_value)
        ok_cell.fill = dark_green_fill
        ok_cell.font = white_font
        ok_cell.alignment = center_alignment
        
        # IY 시트 헤더
        iy_cell = ws_iy.cell(row=1, column=col, value=header_value)
        iy_cell.fill = dark_green_fill
        iy_cell.font = white_font
        iy_cell.alignment = center_alignment
    
    # 열 너비 복사
    for col in range(1, len(headers) + 1):
        col_letter = get_column_letter(col)
        src_width = ws_source.column_dimensions[col_letter].width
        ws_ok.column_dimensions[col_letter].width = src_width
        ws_iy.column_dimensions[col_letter].width = src_width
    
    # 행 높이 설정
    ws_ok.row_dimensions[1].height = 15
    ws_iy.row_dimensions[1].height = 15
    
    print("10-1단계: 시트 분리 준비 완료")
    
    # ================================
    # [10-2] 데이터 분류 및 복사
    # ================================
    
    ok_row = 2
    iy_row = 2
    font = Font(name='맑은 고딕', size=9)
    
    # 정렬된 데이터를 원본 시트에 다시 입력하고 동시에 분리
    for row in range(2, last_row + 1):
        for col in range(1, len(headers) + 1):
            ws_source.cell(row=row, column=col).value = None
    
    for idx, row_data in df.iterrows():
        excel_row = idx + 2
        
        # 원본 시트에 데이터 입력
        for col_idx, value in enumerate(row_data, 1):
            ws_source.cell(row=excel_row, column=col_idx, value=value)
        
        # B열(사이트 정보)에서 계정명 추출
        site_value = str(row_data.iloc[1]) if pd.notna(row_data.iloc[1]) else ""
        account_name = ""
        
        if "]" in site_value and site_value.startswith("["):
            try:
                account_name = site_value[1:site_value.index("]")]
            except:
                account_name = ""
        
        # 계정명에 따라 시트 분리
        if account_name in ["오케이마트", "클로버즈", "베이지베이글"]:
            # OK,CL,BB 시트에 복사
            for col_idx, value in enumerate(row_data, 1):
                cell = ws_ok.cell(row=ok_row, column=col_idx, value=value)
                cell.font = font
            ws_ok.row_dimensions[ok_row].height = 15
            ok_row += 1
            
        elif account_name == "아이예스":
            # IY 시트에 복사
            for col_idx, value in enumerate(row_data, 1):
                cell = ws_iy.cell(row=iy_row, column=col_idx, value=value)
                cell.font = font
            ws_iy.row_dimensions[iy_row].height = 15
            iy_row += 1
    
    print(f"10-2단계: 데이터 분리 완료 (OK: {ok_row-2}행, IY: {iy_row-2}행)")
    
    # ================================
    # [10-3] A열 수식 값 변환
    # ================================
    
    # 모든 시트의 A열 순번 재설정
    for ws in [ws_source, ws_ok, ws_iy]:
        if ws.max_row > 1:
            for row in range(2, ws.max_row + 1):
                ws[f'A{row}'].value = row - 1
    
    print("10-3단계: A열 순번 재설정 완료")
    
    # ================================
    # [11단계] 모든 시트에서 L열 처리
    # ================================
    
    red_font = Font(color="FF0000")
    
    for ws in workbook.worksheets:
        if ws.max_row <= 1:
            continue
            
        l_last_row = ws.max_row
        for row in range(last_row, 0, -1):
            if ws[f'L{row}'].value is not None:
                l_last_row = row
                break
        
        for row in range(2, l_last_row + 1):
            l_value = ws[f'L{row}'].value
            if l_value:
                l_value_str = str(l_value).strip()
                
                if l_value_str == "신용":
                    ws[f'L{row}'].value = ""
                elif l_value_str == "착불":
                    ws[f'L{row}'].font = red_font
    
    print("11단계: L열 처리 완료 (신용→공백, 착불→빨간색)")
    
    # 모든 시트에 서식 재적용
    apply_formatting_to_all_sheets(workbook)
    
    # 파일 저장
    workbook.save(file_path)
    print(f"9~11단계 처리 완료! 최종 파일: {file_path}")
    
    return file_path

def apply_formatting_to_all_sheets(workbook):
    """
    모든 시트에 서식 재적용
    """
    font = Font(name='맑은 고딕', size=9)
    center_alignment = Alignment(horizontal='center')
    right_alignment = Alignment(horizontal='right')
    light_blue_fill = PatternFill(start_color="ADD8E6", end_color="ADD8E6", fill_type="solid")
    
    for ws in workbook.worksheets:
        if ws.max_row <= 1:
            continue
            
        # 기본 폰트 적용
        for row in range(1, ws.max_row + 1):
            ws.row_dimensions[row].height = 15
            for col in range(1, ws.max_column + 1):
                ws.cell(row=row, column=col).font = font
        
        # 정렬 적용
        for row in range(2, ws.max_row + 1):
            if ws.max_column >= 1:
                ws[f'A{row}'].alignment = center_alignment
            if ws.max_column >= 2:
                ws[f'B{row}'].alignment = center_alignment
            if ws.max_column >= 4:
                ws[f'D{row}'].alignment = right_alignment
            if ws.max_column >= 5:
                ws[f'E{row}'].alignment = right_alignment
            if ws.max_column >= 7:
                ws[f'G{row}'].alignment = right_alignment
        
        # F열 조건부 서식 재적용
        for row in range(2, ws.max_row + 1):
            if ws.max_column >= 6:
                f_value = ws[f'F{row}'].value
                cell_value = str(f_value).strip() if f_value else ""
                
                should_highlight = False
                
                if cell_value == "" or cell_value == "None":
                    should_highlight = True
                elif cell_value and all(c == '#' for c in cell_value):
                    should_highlight = True
                elif cell_value.endswith("개") and cell_value[:-1].isdigit():
                    should_highlight = True
                
                if should_highlight:
                    ws[f'F{row}'].fill = light_blue_fill

def gok_erp_automation_full(file_path):
    """
    G,옥 ERP 자동화 전체 프로세스 실행
    
    Args:
        file_path (str): 처리할 Excel 파일 경로
    """
    
    print("G,옥 ERP 자동화 전체 프로세스 시작...")
    
    # 1~8단계 실행
    step1_8_file = gmarket_auction_erp_1_to_8(file_path)
    
    # 9~11단계 실행
    final_file = run_steps_9_to_11(step1_8_file)
    
    print(f"✓ G,옥 ERP 자동화 완료! 최종 파일: {final_file}")
    return final_file

def create_processing_summary(file_path):
    """
    처리 결과 요약 생성
    """
    workbook = openpyxl.load_workbook(file_path)
    
    summary = {}
    
    for ws in workbook.worksheets:
        sheet_name = ws.title
        row_count = ws.max_row - 1 if ws.max_row > 1 else 0
        
        # 바구니 중복 제거 통계 (원본 시트에서만)
        basket_count = 0
        jeju_count = 0
        
        if sheet_name == workbook.worksheets[0].title:  # 원본 시트
            # Q열 바구니 번호 카운트
            basket_numbers = set()
            for row in range(2, ws.max_row + 1):
                q_value = ws[f'Q{row}'].value
                if q_value:
                    basket_numbers.add(str(q_value).strip())
            basket_count = len(basket_numbers)
        
        summary[sheet_name] = {
            'rows': row_count,
            'baskets': basket_count if basket_count > 0 else 'N/A'
        }
    
    print("\n" + "="*50)
    print("G,옥 ERP 자동화 처리 결과 요약")
    print("="*50)
    
    for sheet_name, info in summary.items():
        print(f"시트 '{sheet_name}': {info['rows']:,}행")
        if info['baskets'] != 'N/A':
            print(f"  - 바구니 수: {info['baskets']:,}개")
    
    print("="*50)
    return file_path

# 사용 예시
if __name__ == "__main__":
    # 파일 경로를 지정하세요
    excel_file_path = "your_gok_file.xlsx"
    
    try:
        # G,옥 ERP 자동화 전체 프로세스 실행
        final_file = gok_erp_automation_full(excel_file_path)
        
        # 처리 결과 요약
        create_processing_summary(final_file)
        
        print("G,옥 ERP 자동화가 성공적으로 완료되었습니다!")
        
    except Exception as e:
        print(f"오류가 발생했습니다: {e}")
        import traceback
        traceback.print_exc()