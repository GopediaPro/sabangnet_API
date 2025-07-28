import pandas as pd
import os
import sys
from datetime import datetime

def merge_excel_sheets(file1_path, file2_path, output_file_path):
    """
    두 개의 엑셀 파일의 모든 시트를 읽어와 하나의 새로운 엑셀 파일로 합칩니다.

    Args:
        file1_path (str): 첫 번째 엑셀 파일의 경로.
        file2_path (str): 두 번째 엑셀 파일의 경로.
        output_file_path (str): 결과를 저장할 새로운 엑셀 파일의 경로.
    """
    try:
        # 첫 번째 엑셀 파일의 모든 시트 읽기
        xls1 = pd.ExcelFile(file1_path)
        sheets1 = {sheet_name: xls1.parse(sheet_name) for sheet_name in xls1.sheet_names}
        print(f"'{file1_path}'에서 {len(sheets1)}개의 시트를 읽었습니다.")

        # 두 번째 엑셀 파일의 모든 시트 읽기
        xls2 = pd.ExcelFile(file2_path)
        sheets2 = {sheet_name: xls2.parse(sheet_name) for sheet_name in xls2.sheet_names}
        print(f"'{file2_path}'에서 {len(sheets2)}개의 시트를 읽었습니다.")

        # 새로운 엑셀 파일에 쓰기 위한 ExcelWriter 객체 생성
        with pd.ExcelWriter(output_file_path, engine='xlsxwriter') as writer:
            # 첫 번째 파일의 시트들을 새로운 파일에 쓰기
            for sheet_name, df in sheets1.items():
                new_sheet_name = f"{sheet_name}_r"
                df.to_excel(writer, sheet_name=new_sheet_name, index=False)
                print(f"'{sheet_name}' 시트가 '{new_sheet_name}'로 '{output_file_path}'에 추가되었습니다.")

            # 두 번째 파일의 시트들을 새로운 파일에 쓰기
            # 만약 시트 이름이 중복된다면, 뒤에 '_m'를 붙여서 구분할 수 있습니다.
            # 이 부분은 필요에 따라 조정할 수 있습니다.
            for sheet_name, df in sheets2.items():
                new_sheet_name = f"{sheet_name}_m"
                df.to_excel(writer, sheet_name=new_sheet_name, index=False)
                print(f"'{sheet_name}' 시트가 '{new_sheet_name}'으로 '{output_file_path}'에 추가되었습니다.")

        print(f"\n모든 시트가 성공적으로 '{output_file_path}' 파일에 합쳐졌습니다.")

    except FileNotFoundError:
        print("에러: 지정된 파일 경로를 찾을 수 없습니다. 파일 경로를 확인해 주세요.")
    except Exception as e:
        print(f"엑셀 파일을 처리하는 동안 오류가 발생했습니다: {e}")

# --- 사용 예시 ---
if __name__ == "__main__":
    # 테스트를 위한 예시 엑셀 파일 생성 (실제 사용 시에는 이 부분은 필요 없습니다)
    try:
        """
        # file1.xlsx 생성
        df1_sheet1 = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
        df1_sheet2 = pd.DataFrame({'X': ['a', 'b'], 'Y': ['c', 'd']})
        with pd.ExcelWriter(file1_path, engine='xlsxwriter') as writer:
            df1_sheet1.to_excel(writer, sheet_name='Sheet1_A', index=False)
            df1_sheet2.to_excel(writer, sheet_name='Sheet2_B', index=False)
        print(f"테스트 파일 '{file1_path}' 생성 완료.")

        # file2.xlsx 생성
        df2_sheet1 = pd.DataFrame({'C': [5, 6], 'D': [7, 8]})
        df2_sheet2 = pd.DataFrame({'Z': [9, 10], 'W': [11, 12]})
        df2_sheet3_dup = pd.DataFrame({'Dup': ['foo', 'bar']}) # 중복 시트 이름 테스트용
        with pd.ExcelWriter(file2_path, engine='xlsxwriter') as writer:
            df2_sheet1.to_excel(writer, sheet_name='Sheet3_C', index=False)
            df2_sheet2.to_excel(writer, sheet_name='Sheet4_D', index=False)
            df2_sheet3_dup.to_excel(writer, sheet_name='Sheet1_A', index=False) # 중복 시트 이름
        print(f"테스트 파일 '{file2_path}' 생성 완료.")
        """

        if len(sys.argv) > 3:
            # 현재 스크립트가 실행되는 디렉토리를 기준으로 파일 경로 설정
            current_dir = os.path.dirname(os.path.abspath(__file__))
            file1_name = sys.argv[1]
            file2_name = sys.argv[2]
            job_type = sys.argv[3]

            today = datetime.now()
            date_yyyymmdd = today.strftime("%Y%m%d")
            output_file_name = f"{job_type}_merged_excel_{date_yyyymmdd}.xlsx"

            current_dir = f"{current_dir}/{date_yyyymmdd}"

            file1_path = os.path.join(current_dir, file1_name)
            file2_path = os.path.join(current_dir, file2_name)
            output_file_path = os.path.join(current_dir, output_file_name)
            merge_excel_sheets(file1_path, file2_path, output_file_path)
        else:
            print("Usage python rpa_filename macro_filename job_type")

    except Exception as e:
        print(f"테스트 파일 생성 중 오류 발생: {e}")

    finally:
        # 테스트 파일 삭제 (선택 사항)
        # if os.path.exists(file1_path):
        #     os.remove(file1_path)
        # if os.path.exists(file2_path):
        #     os.remove(file2_path)
        # print("\n테스트 파일 삭제 완료.")
        pass