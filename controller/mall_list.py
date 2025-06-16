from sabangnet_handler import SabangNetMallAPI
from file_server_handler import upload_to_file_server, get_file_server_url, upload_xml_content_to_file_server
from pathlib import Path


def fetch_mall_list():
    xml_base_path = Path("./files/xml")
    try:
        api = SabangNetMallAPI()
        print(f"사방넷 쇼핑몰 목록 조회")
        print("=" * 50)
        print("1. 파일(XML) 업로드 후 URL로 호출 (권장)")
        print("2. XML 내용을 직접 업로드 후 URL로 호출")
        print("3. XML URL을 직접 입력하여 호출")
        choice = input("\n선택하세요 (1, 2 또는 3): ").strip()
        if choice == "1":
            # 1. XML 생성 및 파일로 저장
            xml_content = api.create_request_xml()
            xml_base_path.mkdir(exist_ok=True)
            xml_file_path = xml_base_path / "mall_request.xml"
            with open(xml_file_path, 'w', encoding='euc-kr') as f:
                f.write(xml_content)
            print(f"\n요청 XML이 {xml_file_path}에 저장되었습니다.")
            # 파일 서버 업로드
            object_name = upload_to_file_server(xml_file_path)
            print(f"파일 서버에 업로드된 XML 파일 이름: {object_name}")
            xml_url = get_file_server_url(object_name)
            print(f"파일 서버에 업로드된 XML URL: {xml_url}")
            mall_list = api.get_mall_list_via_url(xml_url)
        elif choice == "2":
            # 2. XML 내용을 직접 파일 서버에 업로드
            xml_content = api.create_request_xml()
            filename = input("업로드할 XML 파일명을 입력하세요 (예: mall_request.xml): ").strip()
            if not filename:
                filename = 'mall_request.xml'
            object_name = upload_xml_content_to_file_server(xml_content, filename)
            print(f"파일 서버에 업로드된 XML 파일 이름: {object_name}")
            xml_url = get_file_server_url(object_name)
            print(f"파일 서버에 업로드된 XML URL: {xml_url}")
            mall_list = api.get_mall_list_via_url(xml_url)
        elif choice == "3":
            xml_url = input("\nXML 파일의 URL을 입력하세요 (예: http://www.abc.co.kr/aa.xml): ").strip()
            if not xml_url:
                print("유효한 XML URL을 입력해주세요.")
                return
            mall_list = api.get_mall_list_via_url(xml_url)
            print(f"XML URL 요청 결과: {mall_list}")
        else:
            print("잘못된 선택입니다.")
            return
        api.display_mall_list(mall_list)
        print("성공적으로 저장되었습니다. (경로: ./json/mall_list.json)")
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