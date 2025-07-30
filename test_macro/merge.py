import pandas as pd
import os
import sys
from datetime import datetime
import gc

def merge_excel_sheets(file1_path, file2_path, output_file_path):
    """
    두 개의 엑셀 파일의 모든 시트를 읽어와 하나의 새로운 엑셀 파일로 합칩니다.

    Args:
        file1_path (str): 첫 번째 엑셀 파일의 경로.
        file2_path (str): 두 번째 엑셀 파일의 경로.
        output_file_path (str): 결과를 저장할 새로운 엑셀 파일의 경로.
    """
    writer = None  # writer 변수를 미리 정의
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
        writer = pd.ExcelWriter(output_file_path, engine='xlsxwriter') # with문 밖에서 정의
        # with pd.ExcelWriter(output_file_path, engine='xlsxwriter') as writer:
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
    finally:
        if writer:
            writer.close()  # 명시적으로 writer.close() 호출
            del writer       # writer 객체 삭제
            gc.collect()     # 가비지 컬렉션 수행

        print("병합 프로세스가 완료되었습니다.")

# --- 사용 예시 ---
if __name__ == "__main__":
    try:
        if len(sys.argv) > 3:
            # 현재 스크립트가 실행되는 디렉토리를 기준으로 파일 경로 설정
            current_dir = os.path.dirname(os.path.abspath(__file__))
            file1_name = sys.argv[1]
            file2_name = sys.argv[2]
            job_type = str(sys.argv[3]).strip()

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