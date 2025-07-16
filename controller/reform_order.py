from pathlib import Path

def test_reform_macro():
    xlsx_base_path = Path("./files/excel/")
    try:
        print("알리 양식수정 테스트")
        print(f"기본 경로: {xlsx_base_path}")
        print("ex) 20250709_알리원본.xlsx")
        xlsx_file_name = input("ali_express 주문양식: ")
        xlsx_file_path = xlsx_base_path / xlsx_file_name
        if not xlsx_file_path.exists():
            print("파일이 존재하지 않습니다.")
            print(xlsx_file_path)
            return
        xlsx_file_path = str(xlsx_file_path)
        macro_file_path = ""
        from utils.macros.reform_order.ali_reform import reform_order_ali
        macro_file_path = reform_order_ali(xlsx_file_path)

        print("양식 변경 완료")
        print(f"결과 파일 경로: {macro_file_path}")

    except Exception as e:
        print(f"Error: {e}")
    return macro_file_path

