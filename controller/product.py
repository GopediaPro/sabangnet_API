from services.product.product_create_service import ProductCreateService
from file_server_handler import upload_to_file_server, get_file_server_url, upload_xml_content_to_file_server
from utils.sabangnet_logger import get_logger

logger = get_logger(__name__)

# 상품코드 생성 및 test_product_raw_data 저장 실행 함수
import asyncio
from services.product_registration.product_integrated_service import ProductCodeIntegratedService


def request_product_create(file_name: str, sheet_name: str):
    try:
        xml_file_path = ProductCreateService.excel_to_xml_file(file_name, sheet_name)
        logger.info(f"XML 파일 경로: {xml_file_path}")
        print("=" * 50)
        print(f"사방넷 상품등록")
        print("=" * 50)
        # 상품 등록 방법 선택
        print("상품 등록 방법을 선택합니다.")
        print("1. 파일(XML) 업로드 후 URL로 호출 (권장)")
        print("2. XML 내용을 직접 업로드 후 URL로 호출")
        print("3. XML URL을 직접 입력하여 호출")
        choice = input("\n선택하세요 (1, 2 또는 3): ").strip()
        if choice == "1":
            if not xml_file_path.exists():
                raise FileNotFoundError(f"요청 XML이 {xml_file_path}에 존재하지 않습니다.")
            # 파일 서버 업로드
            object_name = upload_to_file_server(xml_file_path)
            print(f"파일 서버에 업로드된 XML 파일 이름: {object_name}")
            xml_url = get_file_server_url(object_name)
            print(f"파일 서버에 업로드된 XML URL: {xml_url}")
            create_product_response = ProductCreateService.request_product_create_via_url(xml_url)
        elif choice == "2":
            # 2. XML 내용을 직접 파일 서버에 업로드
            xml_content = ProductCreateService.excel_to_xml_string(file_name, sheet_name)
            filename = input("업로드할 XML 파일명을 입력하세요 (예: product_create_request.xml): ").strip()
            if not filename:
                filename = xml_file_path
            object_name = upload_xml_content_to_file_server(xml_content, filename)
            print(f"파일 서버에 업로드된 XML 파일 이름: {object_name}")
            xml_url = get_file_server_url(object_name)
            print(f"파일 서버에 업로드된 XML URL: {xml_url}")
            create_product_response = ProductCreateService.request_product_create_via_url(xml_url)
        elif choice == "3":
            xml_url = input("\nXML 파일의 URL을 입력하세요 (예: http://www.abc.co.kr/aa.xml): ").strip()
            if not xml_url:
                print("유효한 XML URL을 입력해주세요.")
                return
            create_product_response = ProductCreateService.request_product_create_via_url(xml_url)
        else:
            print("잘못된 선택입니다.")
            return
        print(f"XML URL 요청 결과: {create_product_response}")
    except ValueError as e:
        print(f"\n환경변수를 확인해주세요: {e}")
        print("- SABANG_COMPANY_ID: 사방넷 로그인 아이디")
        print("- SABANG_AUTH_KEY: 사방넷 인증키")
        print("- SABANG_ADMIN_URL: 사방넷 어드민 URL (선택사항)")
    except Exception as e:
        print(f"\n오류가 발생했습니다: {e}")
        print("\n가능한 해결 방법:")
        print("1. 사방넷 계정 정보가 올바른지 확인")
        print("2. 인증키가 유효한지 확인")
        print("3. 네트워크 연결 상태 확인")
        print("4. XML URL 방식으로 다시 시도")
def run_generate_and_save_all_product_code_data():
    print("\n[상품코드 생성 및 test_product_raw_data 저장 시작]")
    try:
        service = ProductCodeIntegratedService()
        result = asyncio.run(service.generate_and_save_all_product_code_data())
        print("\n=== 처리 결과 ===")
        print(f"성공: {result['success']}")
        print(f"실패: {result['failed']}")
        print("\n[완료]")
    except Exception as e:
        print(f"오류 발생: {e}")