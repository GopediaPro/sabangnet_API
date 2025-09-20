from pathlib import Path
from core.db import get_async_session


async def test_erp_macro():

    xlsx_base_path = Path("./files/excel/erp")
    try:
        print(f"Excel 파일 ERP 매크로 적용 테스트")
        print('=' * 50)
        print("매크로 선택")
        print("1.기타사이트_ERP_자동화")
        print("2.지그재그_ERP_자동화")
        print("3.알리_ERP_자동화")
        print("4.브랜디_ERP_자동화")
        print("5.G,옥_ERP_자동화")
        choice = input("매크로 선택: ")
        print('=' * 50)
        print("Excal 파일 경로 설정")
        print(f"기본 경로: {xlsx_base_path}")
        print("ex) [기본양식]-ERP용.xlsx")
        xlsx_file_name = input("파일명 입력: ")
        xlsx_file_path = xlsx_base_path / xlsx_file_name
        if not xlsx_file_path.exists():
            print(f"파일이 존재하지 않습니다.")
            print(xlsx_file_path)
            return
        xlsx_file_path = str(xlsx_file_path)
        macro_file_path = ""
        if choice == "1":
            # 기타사이트_ERP_자동화
            from utils.macros.ERP.v1.etc_site_macro import ERPEtcSiteMacro

            macro = ERPEtcSiteMacro(xlsx_file_path)
            macro_file_path = macro.etc_site_macro_run()

            print("기타사이트_ERP_자동화")

        elif choice == "2":
            # 지그재그_ERP_자동화
            from utils.macros.ERP.v1.zigzag_erp_macro import ERPZigzagMacro

            zigzag_macro = ERPZigzagMacro(xlsx_file_path)
            macro_file_path = zigzag_macro.zigzag_erp_macro_run()

            print("지그재그_ERP_자동화")

        elif choice == "3":
            # 알리_ERP_자동화
            from utils.macros.ERP.v1.ali_erp_macro import ERPAliMacro

            # 알리 ERP 자동화 전체 프로세스 실행
            ali_macro = ERPAliMacro(xlsx_file_path)
            macro_file_path = ali_macro.ali_erp_macro_run()

            print("알리_ERP_자동화")

        elif choice == "4":
            # 브랜디_ERP_자동화
            from utils.macros.ERP.v1.brandi_erp_macro import ERPBrandiMacro

            # 브랜디 ERP 자동화 전체 프로세스 실행
            brandi_macro = ERPBrandiMacro(xlsx_file_path)
            macro_file_path = brandi_macro.brandi_erp_macro_run()

            print("브랜디_ERP_자동화")

        elif choice == "5":
            # down_form_order table to excel

            from utils.macros.ERP.v1.g_a_erp_macro import ERPGmaAucMacro
            # # G,옥_ERP_자동화
            gmarket_auction_macro = ERPGmaAucMacro(xlsx_file_path)
            macro_file_path = gmarket_auction_macro.gauc_erp_macro_run()

            print("G,옥 ERP 자동화")

        else:
            print("매크로를 선택헤 주세요. 1~5")
            return

        print("매크로 적용 완료")
        print(f"경로 : {macro_file_path}")

    except Exception as e:
        print(f"Error: {e}")
    return
