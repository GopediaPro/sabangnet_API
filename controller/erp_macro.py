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
            from utils.macros.ERP.etc_site_macro import ECTSiteMacro

            macro = ECTSiteMacro(xlsx_file_path)
            macro_file_path = macro.step_1_to_14()

            print("기타사이트_ERP_자동화")

        elif choice == "2":
            # 지그재그_ERP_자동화
            from utils.macros.ERP.zigzag_erp_macro import ZigzagMacro

            zigzag_macro = ZigzagMacro(xlsx_file_path)
            macro_file_path = zigzag_macro.step_1_to_9()

            print("지그재그_ERP_자동화")

        elif choice == "3":
            # 알리_ERP_자동화
            from utils.macros.ERP.ali_erp_macro import AliMacro

            # 알리 ERP 자동화 전체 프로세스 실행
            ali_macro = AliMacro(xlsx_file_path)
            macro_file_path = ali_macro.step_1_to_10()

            print("알리_ERP_자동화")

        elif choice == "4":
            # 브랜디_ERP_자동화
            from utils.macros.ERP.brandi_erp_macro import BrandiMacro

            # 브랜디 ERP 자동화 전체 프로세스 실행
            brandi_macro = BrandiMacro(xlsx_file_path)
            macro_file_path = brandi_macro.step_1_to_11()

            print("브랜디_ERP_자동화")

        elif choice == "5":
            # down_form_order table to excel
            from utils.macros.ERP.Gmarket_auction_erp_macro import GmarketAuctionMacro
            from services.usecase.down_form_order_save_usecase import DownFormOrderSaveUsecase
            down_form_order_save_usecase = DownFormOrderSaveUsecase(await get_async_session())
            file_path = await down_form_order_save_usecase.down_form_order_to_excel(template_code="gmarket_erp", file_path="./files/excel/er", file_name="gmarket_erp")

            # # G,옥_ERP_자동화
            gmarket_auction_macro = GmarketAuctionMacro(file_path)
            macro_file_path = gmarket_auction_macro.step_1_to_11()

            print("G,옥 ERP 자동화")

        else:
            print("매크로를 선택헤 주세요. 1~5")
            return

        print("매크로 적용 완료")
        print(f"경로 : {macro_file_path}")

    except Exception as e:
        print(f"Error: {e}")
    return
