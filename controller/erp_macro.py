from pathlib import Path


def test_erp_macro():
    xlsx_base_path = Path("./files/xlsx/")
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
            from utils.macros.ERP.other_site_macro import other_site_macro_1_to_14, apply_conditional_formatting

            # 매크로 실행
            processed_file = other_site_macro_1_to_14(xlsx_file_path)

            # 조건부 서식 적용
            macro_file_path = apply_conditional_formatting(processed_file)

            print("기타사이트_ERP_자동화")

        elif choice == "2":
            # 지그재그_ERP_자동화
            from utils.macros.ERP.zigzag_erp_macro import zigzag_erp_automation_full, apply_advanced_formatting

            # 전체 자동화 프로세스 실행
            final_file = zigzag_erp_automation_full(xlsx_file_path)

            # 고급 서식 적용
            macro_file_path = apply_advanced_formatting(final_file)

            print("지그재그_ERP_자동화")

        elif choice == "3":
            # 알리_ERP_자동화
            from utils.macros.ERP.ali_erp_macro import ali_erp_macro_1_to_15, apply_additional_formatting

            # 알리 ERP 자동화 전체 프로세스 실행
            processed_file = ali_erp_macro_1_to_15(xlsx_file_path, sheet_name="자동화")
            
            # 추가 서식 적용
            macro_file_path = apply_additional_formatting(processed_file)
            
            print("알리_ERP_자동화")
        
        elif choice == "4":
            # 브랜디_ERP_자동화
            from utils.macros.ERP.brandi_erp_macro import brandi_erp_macro_1_to_10,create_summary_report, validate_processing_result
            
            # 브랜디 ERP 자동화 전체 프로세스 실행
            processed_file = brandi_erp_macro_1_to_10(xlsx_file_path)
            
            # 처리 결과 요약 보고서 생성
            macro_file_path = create_summary_report(processed_file)
            
            # 처리 결과 검증
            validation_results = validate_processing_result(processed_file)
            
            print("\n처리 결과 검증:")
            for key, result in validation_results.items():
                status = "✓ 성공" if result else "✗ 실패"
                print(f"- {key}: {status}")
            
            if all(validation_results.values()):
                print("\n✓ 모든 검증 통과! 브랜디 ERP 자동화가 성공적으로 완료되었습니다.")
            else:
                print("\n 일부 검증 실패. 결과를 확인해주세요.")
                print("브랜디_ERP_자동화")
            
            print("브랜디_ERP_자동화")
        
        elif choice =="5":
            # G,옥_ERP_자동화
            from utils.macros.ERP.Gmarket_auction_erp_macro import gok_erp_automation_full, create_processing_summary

            final_file = gok_erp_automation_full(xlsx_file_path)
        
            # 처리 결과 요약
            macro_file_path = create_processing_summary(final_file)
            
            print("G,옥 ERP 자동화")
        
        else:
            print("매크로를 선택헤 주세요. 1~5")
            return

        print("매크로 적용 완료")
        print(f"경로 : {macro_file_path}")

    except Exception as e:
        print(f"Error: {e}")
    return
