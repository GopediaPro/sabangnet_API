import xlwings as xw

def compare_excel_with_xlwings(excel_filename, compares, red_color_rgb=(255, 0, 0)):
    try:
        # Excel 애플리케이션 열기 (visible=False로 백그라운드 실행 가능)
        # visible=True로 바꾸면 Excel 창이 직접 보이는 것을 확인할 수 있습니다.
        app = xw.App(visible=False) # 테스트 시에는 visible=True로 두어 눈으로 확인하는 것이 좋습니다.
        wb = app.books.open(excel_filename)

        print("--- 시트 데이터 비교 시작 (xlwings) ---")
        for compare in compares:
            sheet1_name = compare["sheet1_name"]
            sheet2_name = compare["sheet2_name"]

            if sheet1_name not in wb.sheetnames or sheet2_name not in wb.sheetnames:
                print(f"경고: '{sheet1_name}' 또는 '{sheet2_name}' 시트가 워크북에 없습니다. 건너뜝니다.")
                continue

            sheet1 = wb.sheets[sheet1_name]
            sheet2 = wb.sheets[sheet2_name]

            # 모든 셀의 배경색 초기화 (선택 사항, 필요하다면)
            # 이전에 openpyxl에서 문제가 됐던 배경색 초기화도 xlwings에서는 안전합니다.
            # sheet1.cells.api.Interior.ColorIndex = 0 # 색상 없음 (기존)
            # sheet2.cells.api.Interior.ColorIndex = 0
            # 또는 RGB를 직접 사용할 수도 있습니다. (예: (255,255,255)는 흰색)
            last_row1 = sheet1.api.UsedRange.Rows.Count
            last_col1 = sheet1.api.UsedRange.Columns.Count
            if last_row1 >= 2 and last_col1 >= 1:
                sheet1.range(sheet1.cells(2,1), sheet1.cells(last_row1, last_col1)).color = None # 배경색 초기화

            last_row2 = sheet2.api.UsedRange.Rows.Count
            last_col2 = sheet2.api.UsedRange.Columns.Count
            if last_row2 >= 2 and last_col2 >= 1:
                sheet2.range(sheet2.cells(2,1), sheet2.cells(last_row2, last_col2)).color = None # 배경색 초기화


            max_row = max(sheet1.api.UsedRange.Rows.Count, sheet2.api.UsedRange.Rows.Count)
            max_col = max(sheet1.api.UsedRange.Columns.Count, sheet2.api.UsedRange.Columns.Count)
            found_diff = False

            for row_idx in range(1, max_row + 1):
                for col_idx in range(1, max_col + 1):
                    cell1 = sheet1.cells(row_idx, col_idx)
                    cell2 = sheet2.cells(row_idx, col_idx)

                    value1 = cell1.value
                    value2 = cell2.value
                    formula1 = cell1.formula # 수식 자체를 가져옴
                    formula2 = cell2.formula # 수식 자체를 가져옴

                    # 값 또는 수식 불일치 확인
                    is_diff = False
                    if formula1 is not None and formula2 is not None: # 둘 다 수식일 경우 수식 문자열 비교
                        if formula1 != formula2:
                            is_diff = True
                    elif formula1 is None and formula2 is None: # 둘 다 값이면 값 비교
                        if value1 != value2:
                            is_diff = True
                    else: # 하나는 수식, 하나는 값 등 타입 자체가 다른 경우 (불일치)
                        is_diff = True

                    if is_diff:
                        found_diff = True
                        display_content1 = f"수식: '{formula1}'" if formula1 else f"값: '{value1}'"
                        display_content2 = f"수식: '{formula2}'" if formula2 else f"값: '{value2}'"

                        print(f"불일치 발견: 시트1 [{row_idx}행, {col_idx}열] {display_content1}, "
                              f"시트2 [{row_idx}행, {col_idx}열] {display_content2}")
                        cell1.color = red_color_rgb # 불일치 셀에 배경색 설정

            if not found_diff:
                print(f"'{sheet1_name}' 와 '{sheet2_name}' 시트 간 불일치 없음.")
            print("\n")

        # 변경사항 저장
        wb.save()
        print(f"비교 및 변경 완료. 결과 파일은 '{excel_filename}'에 저장되었습니다.")

    except Exception as e:
        print(f"xlwings 실행 중 오류 발생: {e}")
        # 오류 발생 시 Excel 앱이 열려있을 수 있으므로 강제 종료
    finally:
        if 'wb' in locals() and wb:
            try:
                wb.close()
            except Exception as e:
                print(f"워크북 닫기 중 오류 발생: {e}")
        if 'app' in locals() and app.alive: # app 객체가 존재하고 실행 중이라면
            try:
                app.quit() # Excel 애플리케이션 종료
            except Exception as e:
                print(f"Excel 앱 종료 중 오류 발생: {e}")
        print("--- xlwings 작업 종료 ---")
        return True


# --- 사용 예시 ---
if __name__ == "__main__":
    excel_file = "e_er_data_compare.xlsx"
    red_color = (255, 0, 0) # 빨간색 RGB 값
    compares = []
    compares.append({'sheet1_name':"20250707_주문서확인처리_ 기본양식 -ERP용", 'sheet2_name':"자동화_m"})
    compares.append({'sheet1_name':"OK", 'sheet2_name':"OK_m"})
    compares.append({'sheet1_name':"IY", 'sheet2_name':"IY_m"})
    compares.append({'sheet1_name':"BB", 'sheet2_name':"BB_m"})

    compare_excel_with_xlwings(excel_file, compares, red_color)