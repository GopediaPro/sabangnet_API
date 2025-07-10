from pathlib import Path
from core.db import AsyncSession
from utils.sabangnet_logger import get_logger
from services.order.order_create_service import OrderCreateService
from schemas.order.response.order_response import OrderBulkCreateResponse
from utils.validators.order_validators import is_start_valid_yyyymmdd, is_end_valid_yyyymmdd, is_valid_order_status, OrderDateRangeException, OrderStatusException


logger = get_logger(__name__)


def get_order_date_range():
    print("주문수집일의 범위를 입력하세요 (예: 20250602~20250606)")
    order_date_range = input("일주일 이전의 날짜 범위 권장: ")
    ord_raw_date = order_date_range.split("~")
    is_start_valid_yyyymmdd(ord_raw_date[0])
    is_end_valid_yyyymmdd(ord_raw_date[0], ord_raw_date[1])
    ord_st_date = ord_raw_date[0]
    ord_ed_date = ord_raw_date[1]
    return ord_st_date, ord_ed_date


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
    is_valid_order_status(order_status, allow_new_order=False)
    return order_status


async def fetch_order_list(session: AsyncSession):
    try:
        print("=" * 50)
        ord_st_date, ord_ed_date = get_order_date_range()
        print("\n"*50)
        print("-"*50)
        order_status = get_order_status()
        print("-"*50)
        order_create_service = OrderCreateService(session)
        print("\n"*50)
        # 주문 수집 방법 선택
        print("주문 수집 방법을 선택합니다.")
        print("1. 파일(XML) 업로드 후 URL로 호출 (권장)")
        print("2. XML URL을 직접 입력하여 호출")
        choice = input("\n선택하세요 (1 또는 2): ").strip()
        if choice == "1":
            # XML 생성 및 파일로 저장
            xml_file_path = order_create_service.create_request_xml(ord_st_date, ord_ed_date, order_status)
            # 파일 서버 업로드
            object_name = order_create_service.get_xml_url_from_minio(xml_file_path)
            # 주문 수집
            xml_content = order_create_service.get_orders_from_sabangnet(object_name)
            # 주문 수집 결과 파싱
            order_bulk_create_response: OrderBulkCreateResponse = await order_create_service.save_orders_to_db_from_xml(xml_content)
            # 주문 수집 결과 출력
            logger.info(f"주문 수집 결과: {order_bulk_create_response}")
        elif choice == "2":
            xml_url = input("\nXML 파일의 URL을 입력하세요 (예: http://www.abc.co.kr/aa.xml): ").strip()
            if not xml_url:
                print("유효한 XML URL을 입력해주세요.")
                return
            xml_content = order_create_service.get_orders_from_sabangnet(xml_url)
            order_bulk_create_response: OrderBulkCreateResponse = await order_create_service.save_orders_to_db_from_xml(xml_content)
            logger.info(f"주문 수집 결과: {order_bulk_create_response}")
        else:
            print("잘못된 선택입니다.")
            return
    except ValueError as e:
        print(f"\n환경변수를 확인해주세요: {e}")
        print("- SABANG_COMPANY_ID: 사방넷 로그인 아이디")
        print("- SABANG_AUTH_KEY: 사방넷 인증키")
        print("- SABANG_ADMIN_URL: 사방넷 어드민 URL (선택사항)")
    except OrderDateRangeException as e:
        logger.error(f"\n{e}")
    except OrderStatusException as e:
        logger.error(f"\n{e}")
    except Exception as e:
        print(f"\n오류가 발생했습니다: {e}")
        print("\n가능한 해결 방법:")
        print("1. 사방넷 계정 정보가 올바른지 확인")
        print("2. 인증키가 유효한지 확인")
        print("3. 네트워크 연결 상태 확인")
        print("4. XML URL 방식으로 다시 시도")