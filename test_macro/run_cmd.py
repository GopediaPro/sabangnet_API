import subprocess
import shlex # 인자 파싱을 위해 shlex를 사용하는 것이 안전합니다.
from datetime import datetime

def run_command_script(input_file_path):
    """
    텍스트 파일에서 데이터를 읽어 merge.py를 호출합니다.

    Args:
        input_file_path (str): 입력 텍스트 파일 경로
        merge_script_path (str): 호출할 merge.py 스크립트 경로
    """
    try:
        with open(input_file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                # 각 줄의 앞뒤 공백 및 줄바꿈 문자 제거
                clean_line = line.strip()

                # 주석 처리된 줄 또는 빈 줄은 건너뛰기
                if not clean_line or clean_line.startswith(';'):
                    continue

                # 빈 줄은 건너뛰기
                if not clean_line:
                    continue

                # 공백을 기준으로 분리
                parts = clean_line.split()

                # 예상되는 인자 개수 확인 (type, rpa, macro 총 3개)
                if len(parts) != 3:
                    print(f"경고: {input_file_path} 파일의 {line_num}번째 줄 형식이 올바르지 않습니다: '{clean_line}'. 건너뜁니다.")
                    continue

                # 인자 순서에 맞게 변수에 할당
                current_type = parts[0]
                current_rpa = parts[1]
                current_macro = parts[2]

                # merge.py에 전달할 인자 순서를 맞춰줍니다: rpa, macro, type
                # 예: python merge.py rpa1 macro1 type1
                command_args = [current_rpa, current_macro, current_type]

                # 명령 구성
                # sys.executable은 현재 파이썬 인터프리터 경로를 사용합니다.
                command = [
                    "python", # 또는 sys.executable
                    "merge.py"
                ] + command_args

                # 명령 실행 및 출력
                print(f"\n명령 실행: {' '.join(command)}")
                
                # subprocess.run()을 사용하여 외부 명령 실행
                # check=True: 명령 실행 실패 시 CalledProcessError 발생
                # text=True: 표준 출력/오류를 텍스트로 캡처
                # capture_output=True: 표준 출력/오류를 변수에 저장
                result = subprocess.run(command, capture_output=True, text=True, check=True)

                #print("---------------------")
                #print("Merge 스크립트 실행 결과:")
                #print(f"Standard Output:\n{result.stdout.strip()}")
                #if result.stderr:
                #    print(f"Standard Error:\n{result.stderr.strip()}")
                #print("---------------------")

                today = datetime.now()
                date_yyyymmdd = today.strftime("%Y%m%d")

                command = [
                    "python", # 또는 sys.executable
                    "cmp.py",
                    f"{current_type}_merged_excel_{date_yyyymmdd}.xlsx"
                ]
                result = subprocess.run(command, capture_output=True, text=True, check=True)

    except FileNotFoundError:
        print(f"오류: '{input_file_path}' 파일을 찾을 수 없습니다.")
    except subprocess.CalledProcessError as e:
        print(f"오류: merge.py 스크립트 실행 중 문제가 발생했습니다. 종료 코드: {e.returncode}")
        print(f"STDOUT:\n{e.stdout}")
        print(f"STDERR:\n{e.stderr}")
    except Exception as e:
        print(f"예상치 못한 오류 발생: {e}")

# --- 사용 예시 ---
if __name__ == "__main__":
    # 이 스크립트를 실행할 때, input.txt 파일과 merge.py 파일이 같은 디렉토리에 있다고 가정합니다.
    # 또는 각 파일의 전체 경로를 지정할 수 있습니다.
    input_text_file = "input.txt"

    run_command_script(input_text_file)