from pathlib import Path
from datetime import datetime
from utils.sabangnet_logger import get_logger
from services.order_list_fetch import OrderListFetchService
from file_server_handler import upload_to_file_server, get_file_server_url, upload_xml_content_to_file_server


logger = get_logger(__name__)


class OrderDateRangeException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class OrderStatusException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


def is_valid_yyyymmdd(date_str: str) -> bool:
    # 길이 검사 + 숫자만 포함하는지 확인
    if len(date_str) != 8 or not date_str.isdigit():
        raise OrderDateRangeException(date_str)

    # 날짜 유효성 검사
    try:
        datetime.strptime(date_str, "%Y%m%d")
    except ValueError:
        raise OrderDateRangeException(date_str)


def get_order_date_range():
    print("주문수집일의 범위를 입력하세요 (예: 20250603~20250610)")
    order_date_range = input("일주일 이전의 날짜 범위 권장: ")
    ord_raw_date = order_date_range.split("~")
    is_valid_yyyymmdd(ord_raw_date[0])
    is_valid_yyyymmdd(ord_raw_date[1])
    ord_st_date = ord_raw_date[0]
    ord_ed_date = ord_raw_date[1]
    return ord_st_date, ord_ed_date


def is_valid_order_status(order_status: str) -> bool:

    if order_status in ["001", "002", "003"]:
        raise OrderStatusException(order_status)
    elif order_status in ["004", "006", "007", "008", "009", "010", "011", "012", "021", "022", "023", "024", "025", "026", "999"]:
        return True
    else:
        raise OrderStatusException(order_status)


def get_order_status():
    print("상태코드 목록\n")
    print("""
001\t신규주문\t사용금지
002\t주문확인\t사용금지
003\t출고대기\t사용금지
004\t출고완료
006\t배송보류
007\t취소접수
008\t교환접수
009\t반품접수
010\t취소완료
011\t교환완료
012\t반품완료
021\t교환발송준비
022\t교환발송완료
023\t교환회수준비
024\t교환회수완료
025\t반품회수준비
026\t반품회수완료
999\t폐기""")
    print("-"*50)
    order_status = input("어떤 상태의 주문을 수집할지 입력하세요: ").strip()
    is_valid_order_status(order_status)
    return order_status


def select_order_save_method() -> bool:
    print("\n주문 데이터 저장 방식을 선택하세요:")
    print("1. DB에 저장 (권장)")
    print("2. JSON 파일로 저장")
    method = input("선택하세요 (1 또는 2): ").strip()
    if method == "1":
        return True
    elif method == "2":
        return False
    else:
        print("잘못된 선택입니다. 기본값(JSON 저장)으로 진행합니다.")
        return False


def fetch_order_list():
    xml_base_path = Path("./files/xml")
    try:
        print("사방넷 주문수집")
        print("=" * 50)
        ord_st_date, ord_ed_date = get_order_date_range()
        print("\n"*50)
        print("-"*50)
        order_status = get_order_status()
        print("-"*50)
        fetcher = OrderListFetchService(ord_st_date, ord_ed_date, order_status)
        print("\n"*50)
        # 주문 수집 방법 선택
        print("주문 수집 방법을 선택합니다.")
        print("1. 파일(XML) 업로드 후 URL로 호출 (권장)")
        print("2. XML 내용을 직접 업로드 후 URL로 호출")
        print("3. XML URL을 직접 입력하여 호출")
        choice = input("\n선택하세요 (1, 2 또는 3): ").strip()
        to_db = select_order_save_method()
        if choice == "1":
            # 1. XML 생성 및 파일로 저장
            xml_content = fetcher.create_request_xml()
            xml_base_path.mkdir(exist_ok=True)
            xml_file_path = xml_base_path / "order_list_request.xml"
            with open(xml_file_path, 'w', encoding='euc-kr') as f:
                f.write(xml_content)
            print(f"\n요청 XML이 {xml_file_path}에 저장되었습니다.")
            # 파일 서버 업로드
            object_name = upload_to_file_server(xml_file_path)
            logger.info(f"파일 서버에 업로드된 XML 파일 이름: {object_name}")
            xml_url = get_file_server_url(object_name)
            logger.info(f"파일 서버에 업로드된 XML URL: {xml_url}")
            result = fetcher.get_order_list_via_url(xml_url, to_db=to_db)
        elif choice == "2":
            # 2. XML 내용을 직접 파일 서버에 업로드
            xml_content = fetcher.create_request_xml()
            filename = input("업로드할 XML 파일명을 입력하세요 (예: order_list_request.xml): ").strip()
            if not filename:
                filename = xml_base_path / "order_list_request.xml"
            object_name = upload_xml_content_to_file_server(xml_content, filename)
            logger.info(f"파일 서버에 업로드된 XML 파일 이름: {object_name}")
            xml_url = get_file_server_url(object_name)
            logger.info(f"파일 서버에 업로드된 XML URL: {xml_url}")
            result = fetcher.get_order_list_via_url(xml_url, to_db=to_db)
        elif choice == "3":
            xml_url = input("\nXML 파일의 URL을 입력하세요 (예: http://www.abc.co.kr/aa.xml): ").strip()
            if not xml_url:
                print("유효한 XML URL을 입력해주세요.")
                return
            result = fetcher.get_order_list_via_url(xml_url, to_db=to_db)
            if not to_db:
                logger.info(f"XML URL 요청 결과: {result}")
        else:
            print("잘못된 선택입니다.")
            return
        if to_db:
            print("성공적으로 DB에 저장되었습니다.")
        else:
            print("성공적으로 저장되었습니다. (경로: ./json/order_list.json)")
    except ValueError as e:
        print(f"\n환경변수를 확인해주세요: {e}")
        print("- SABANG_COMPANY_ID: 사방넷 로그인 아이디")
        print("- SABANG_AUTH_KEY: 사방넷 인증키")
        print("- SABANG_ADMIN_URL: 사방넷 어드민 URL (선택사항)")
    except OrderDateRangeException as e:
        print(f"\n올바른 날짜 범위를 입력해주세요 (입력된 날짜 범위: {e})")
    except OrderStatusException as e:
        print(f"\n올바른 상태코드를 입력해주세요 (입력된 상태코드: {e})")
    except Exception as e:
        print(f"\n오류가 발생했습니다: {e}")
        print("\n가능한 해결 방법:")
        print("1. 사방넷 계정 정보가 올바른지 확인")
        print("2. 인증키가 유효한지 확인")
        print("3. 네트워크 연결 상태 확인")
        print("4. XML URL 방식으로 다시 시도")