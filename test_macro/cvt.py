# 기존 코드 (오류 발생 가능성):
# command = [
#     "libreoffice",
#     "--headless",
#     "--convert-to", "xlsx",
#     input_filepath,
#     "--outdir", output_dir
# ]

# 정확한 수정 예시:
# 리스트 내 각 문자열 요소는 독립적으로 따옴표로 묶여야 합니다.
# 또한, try 블록 내부의 모든 코드는 try 문 아래로 일관되게 들여쓰기 되어야 합니다.

import subprocess
import os # os 모듈 임포트 확인

def repair_excel_with_libreoffice(input_filepath, output_filepath):
    try:
        # 이 try 블록 아래의 모든 코드는 들여쓰기 되어야 합니다.
        output_dir = os.path.dirname(output_filepath)
        # output_filename = os.path.basename(output_filepath) # 이 변수는 현재 사용되지 않습니다.

        command = [
            "libreoffice",           # 문자열을 따옴표로 정확히 닫음
            "--headless",            # 문자열을 따옴표로 정확히 닫음
            "--convert-to",          # 문자열을 따옴표로 정확히 닫음
            "xlsx",                  # 문자열을 따옴표로 정확히 닫음
            input_filepath,          # 변수 자체이므로 따옴표 없음
            "--outdir",              # 문자열을 따옴표로 정확히 닫음
            output_dir               # 변수 자체이므로 따옴표 없음
        ]

        print(f"LibreOffice를 사용하여 파일 복구 시도: {' '.join(command)}")
        # check=True를 추가하여 오류 발생 시 CalledProcessError를 발생시킴
        result = subprocess.run(command, capture_output=True, text=True, check=True)

        print(f"LibreOffice stdout: {result.stdout}")
        print(f"LibreOffice stderr: {result.stderr}")

        # LibreOffice는 보통 입력 파일명과 동일하게 출력 파일을 생성하므로,
        # 생성된 파일의 경로를 정확히 파악해야 합니다.
        # input_filepath의 파일명과 output_dir을 합친 경로를 예상합니다.
        converted_file_name = os.path.basename(input_filepath)
        converted_file_path_in_outdir = os.path.join(output_dir, converted_file_name)

        # 만약 최종적으로 원하는 이름이 output_filepath라면, 이름을 변경합니다.
        if converted_file_path_in_outdir != output_filepath:
            # 먼저 기존 output_filepath가 존재하면 삭제 (덮어쓰기 방지)
            if os.path.exists(output_filepath):
                os.remove(output_filepath)
            os.rename(converted_file_path_in_outdir, output_filepath)
            print(f"파일 이름 변경: {converted_file_path_in_outdir} -> {output_filepath}")
        else:
            # 만약 이름이 같아서 rename이 필요 없다면,
            # converted_file_path_in_outdir이 곧 최종 output_filepath임을 확인
            pass # 또는 print(f"파일이 '{output_filepath}'로 성공적으로 생성되었습니다.")


        print(f"'{input_filepath}' 파일이 LibreOffice를 통해 '{output_filepath}'로 복구되었습니다.")
        return True # try 블록이 성공하면 True 반환
    except subprocess.CalledProcessError as e:
        print(f"LibreOffice 실행 중 오류 발생: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False
    except FileNotFoundError:
        print("오류: 'libreoffice' 명령을 찾을 수 없습니다. LibreOffice가 설치되어 있고 PATH에 추가되었는지 확인하세요.")
        return False
    except Exception as e:
        print(f"파일 복구 중 알 수 없는 오류 발생: {e}")
        return False

# # 실제 사용 예시 (기존 openpyxl 코드에 추가)
# # ... (openpyxl로 파일 로드, 비교, 수정 코드) ...
# workbook.save("temp_output_from_openpyxl.xlsx") # openpyxl로 먼저 저장
# 
# # LibreOffice로 다시 저장하여 호환성 높이기
if repair_excel_with_libreoffice("checked_e_er_data_compare.xlsx", "final_e_er_data_compare.xlsx"):
    print("최종 파일이 성공적으로 생성되었습니다.")
else:
    print("LibreOffice를 통한 파일 복구에 실패했습니다.")
# os.remove("temp_output_from_openpyxl.xlsx") # 임시 파일 삭제
