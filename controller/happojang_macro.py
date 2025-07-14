from pathlib import Path
from core.db import get_async_session
from services.usecase.down_form_order_save_usecase import DownFormOrderSaveUsecase


async def test_happojang_macro():
    xlsx_base_path = Path("./files/excel/")
    down_form_order_save_usecase = DownFormOrderSaveUsecase(await get_async_session())
    try:
        print("합포장 자동화 테스트")
        print("=" * 50)
        print("마켓 선택")
        print("1. 기타사이트 합포장")
        print("2. 지그재그 합포장")
        print("3. 알리 합포장")
        print("4. 브랜디 합포장")
        print("5. G,옥 합포장")
        choice = input("마켓 선택: ")
        print("=" * 50)
        print("엑셀 파일 경로 설정")
        print(f"기본 경로: {xlsx_base_path}")

        # TODO: 브랜디, 알리 템플릿 코드 연결시 삭제 필요
        print("ex) test-[기본양식]-합포장용.xlsx")
        xlsx_file_name = input("파일명 입력: ")
        xlsx_file_path = xlsx_base_path / xlsx_file_name
        if not xlsx_file_path.exists():
            print("파일이 존재하지 않습니다.")
            print(xlsx_file_path)
            return
        xlsx_file_path = str(xlsx_file_path)

        macro_file_path = ""

        if choice == "1":

            from utils.macros.happojang.etc_site_merge_packaging import etc_site_merge_packaging
            file_path = await down_form_order_save_usecase.down_form_order_to_excel(
                template_code="basic_bundle",
                file_path="./files/excel", file_name="test_down_form_order"
            )

            macro_file_path = etc_site_merge_packaging(file_path)
            print("기타사이트 합포장 자동화")

        elif choice == "2":

            from utils.macros.happojang.zigzag_merge_packaging import zigzag_merge_packaging
            file_path = await down_form_order_save_usecase.down_form_order_to_excel(template_code="star_basic_erp",
                                                                                file_path="./files/excel",
                                                                                file_name="test_down_form_order")

            macro_file_path = zigzag_merge_packaging(file_path)
            print("지그재그 합포장 자동화")

        elif choice == "3":

            from utils.macros.happojang.ali_merge_packaging import ali_merge_packaging
            # # TODO: 알리 합포장용 템플릿 코드 수정 필요
            # file_path = await down_form_order_to_excel.down_form_order_to_excel(template_code="star_basic_erp",
            #                                                                     file_path="./files/excel",
            #                                                                     file_name="test_down_form_order")

            # macro_file_path = brandy_merge_packaging(file_path)
            macro_file_path = ali_merge_packaging(xlsx_file_path)
            print("알리 합포장 자동화")

        elif choice == "4":
            
            from utils.macros.happojang.brandy_merge_packaging import brandy_merge_packaging
            # TODO: 브랜디 합포장용 템플릿 코드 수정 필요
            # file_path = await down_form_order_to_excel.down_form_order_to_excel(template_code="star_brandi_bundle",
            #                                                                     file_path="./files/excel",
            #                                                                     file_name="test_down_form_order")

            # macro_file_path = brandy_merge_packaging(file_path)
            macro_file_path = brandy_merge_packaging(xlsx_file_path)

            print("브랜디 합포장 자동화")

        elif choice == "5":
            from utils.macros.happojang.gok_merge_packaging import gok_merge_packaging
            file_path = await down_form_order_save_usecase.down_form_order_to_excel(template_code="gmarket_bundle",
                                                                                file_path="./files/excel",
                                                                                file_name="test_down_form_order")

            macro_file_path = gok_merge_packaging(file_path)
            print("G,옥 합포장 자동화")
        else:
            print("마켓을 선택해 주세요. 1~5")
            return

        print("합포장 자동화 완료")
        print(f"결과 파일 경로: {macro_file_path}")

    except Exception as e:
        print(f"Error: {e}")
    return