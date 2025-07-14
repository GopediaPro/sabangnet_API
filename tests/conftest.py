"""
pytest 설정, 픽스처 정의 파일
fatapi 의 main.py 및 다른 설정 파일들과 같은 역할을 함
다른 모듈에서 임포트 하지 않아도 pytest 가 자동으로 인식하고 적용시킴
"""
import os
import pytest
import asyncio

from io import BytesIO
from fastapi import FastAPI
from httpx import AsyncClient
from asyncio import AbstractEventLoop
from fastapi.testclient import TestClient
from typing import Generator, AsyncGenerator, Any
from unittest.mock import AsyncMock, MagicMock, patch

from main import app
from utils.sabangnet_logger import get_logger

logger = get_logger(__name__)


# 테스트 환경 설정
@pytest.fixture(scope="session", autouse=True)
def set_test_environment() -> None:
    """테스트용 더미 환경변수 설정"""
    
    test_env_vars = {
        "SABANG_COMPANY_ID": "test_company",
        "SABANG_AUTH_KEY": "test_auth_key",
        "SABANG_ADMIN_URL": "https://test.example.com",
        "MINIO_ROOT_USER": "test_user",
        "MINIO_ROOT_PASSWORD": "test_password",
        "MINIO_ACCESS_KEY": "test_access_key",
        "MINIO_SECRET_KEY": "test_secret_key",
        "MINIO_ENDPOINT": "localhost:9000",
        "MINIO_BUCKET_NAME": "test-bucket",
        "MINIO_USE_SSL": "false",
        "MINIO_PORT": "9000",
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "DB_NAME": "test_db",
        "DB_USER": "test_user",
        "DB_PASSWORD": "test_password",
        "DB_SSLMODE": "disable",
        "DB_TEST_TABLE": "test_table",
        "DB_TEST_COLUMN": "test_column",
        "FASTAPI_HOST": "localhost",
        "FASTAPI_PORT": "8000",
        "N8N_WEBHOOK_BASE_URL": "https://test.n8n.com",
        "N8N_WEBHOOK_PATH": "test_webhook",
        "CONPANY_GOODS_CD_TEST_MODE": "true"
    }
    
    for key, value in test_env_vars.items():
        os.environ.setdefault(key, value)
    

@pytest.fixture(scope="session")
def event_loop() -> Generator[AbstractEventLoop, Any, None]:
    """이벤트 루프 픽스처 (비동기 테스트용)"""

    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_app() -> FastAPI:
    """FastAPI 앱 픽스처"""

    try:
        # main.py에서 app 임포트됨
        return app
    except Exception as e:
        logger.error(f"fastapi app import 실패: {e}")


@pytest.fixture
def client(test_app: FastAPI) -> Generator[TestClient, Any, None]:
    """동기 테스트 클라이언트"""

    try:
        with TestClient(test_app) as test_client:
            yield test_client
    except Exception as e:
        logger.error(f"동기 테스트 클라이언트 호출 실패: {e}")


@pytest.fixture
async def async_client(test_app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """비동기 테스트 클라이언트"""

    try:
        async with AsyncClient(app=test_app, base_url="http://testserver") as client:
            yield client
    except Exception as e:
        logger.error(f"비동기 테스트 클라이언트 호출 실패: {e}")


@pytest.fixture
def mock_db_session() -> MagicMock:
    """모킹된 데이터베이스 세션"""

    try:
        session = MagicMock()
        session.execute = AsyncMock()
        session.commit = AsyncMock()
        session.rollback = AsyncMock()
        session.close = AsyncMock()
        session.scalar = AsyncMock()
        session.scalars = AsyncMock()
        return session
    except Exception as e:
        logger.error(f"테스트 세션 생성 실패: {e}")


@pytest.fixture(autouse=True)
def mock_database_connections() -> Generator[MagicMock, Any, None]:
    """데이터베이스 연결 모킹 (자동 적용)"""
    
    try:
        with patch('core.db.get_async_session') as mock_session:
            mock_session.return_value = MagicMock()
            yield mock_session
    except Exception as e:
        logger.error(f"테스트 db 연결 실패: {e}")


@pytest.fixture
def sample_product_data() -> dict:
    """샘플 상품 데이터 (ProductRawData 모델 기반)"""

    return {
        "goods_nm": "테스트 상품명",
        "goods_keyword": "테스트, 상품, 키워드",
        "model_nm": "TEST-MODEL-001",
        "model_no": "TEST-MODEL-NO-001",
        "brand_nm": "테스트브랜드",
        "compayny_goods_cd": "TEST_GOODS_001",
        "goods_search": "테스트 상품 검색어",
        "goods_gubun": 1,
        "class_cd1": "TEST_CLASS_1",
        "class_cd2": "TEST_CLASS_2",
        "class_cd3": "TEST_CLASS_3",
        "class_cd4": "TEST_CLASS_4",
        "gubun": "마스터",
        "partner_id": "PARTNER_001",
        "dpartner_id": "DPARTNER_001",
        "maker": "테스트제조사",
        "origin": "국내",
        "make_year": "2024",
        "make_dm": "20240101",
        "goods_season": 1,
        "sex": 0,
        "status": 1,
        "deliv_able_region": 1,
        "tax_yn": 1,
        "delv_type": 1,
        "delv_cost": 3000,
        "banpum_area": 1,
        "goods_cost": 12000,
        "goods_price": 15000,
        "goods_consumer_price": 20000,
        "goods_cost2": 11000,
        "char_1_nm": "색상",
        "char_1_val": "빨강,파랑,노랑",
        "char_2_nm": "사이즈",
        "char_2_val": "S,M,L,XL",
        "img_path": "https://example.com/test-image.jpg",
        "img_path1": "https://example.com/test-image1.jpg",
        "img_path2": "https://example.com/test-image2.jpg",
        "img_path3": "https://example.com/test-image3.jpg",
        "img_path4": "https://example.com/test-image4.jpg",
        "img_path5": "https://example.com/test-image5.jpg",
        "img_path6": "https://example.com/test-image6.jpg",
        "img_path7": "https://example.com/test-image7.jpg",
        "img_path8": "https://example.com/test-image8.jpg",
        "img_path9": "https://example.com/test-image9.jpg",
        "img_path10": "https://example.com/test-image10.jpg",
        "img_path11": "https://example.com/test-image11.jpg",
        "img_path12": "https://example.com/test-image12.jpg",
        "img_path13": "https://example.com/test-image13.jpg",
        "img_path14": "https://example.com/test-image14.jpg",
        "img_path15": "https://example.com/test-image15.jpg",
        "img_path16": "https://example.com/test-image16.jpg",
        "img_path17": "https://example.com/test-image17.jpg",
        "img_path18": "https://example.com/test-image18.jpg",
        "img_path19": "https://example.com/test-image19.jpg",
        "img_path20": "https://example.com/test-image20.jpg",
        "img_path21": "https://example.com/test-image21.jpg",
        "img_path22": "https://example.com/test-image22.jpg",
        "img_path23": "https://example.com/test-image23.jpg",
        "img_path24": "https://example.com/test-image24.jpg",
        "goods_remarks": "테스트 상품 설명입니다.",
        "certno": "TEST-CERT-001",
        "avlst_dm": "20240101",
        "avled_dm": "20241231",
        "issuedate": "20240101",
        "certdate": "20240101",
        "cert_agency": "테스트 인증기관",
        "certfield": "테스트 인증분야",
        "material": "테스트 재료",
        "stock_use_yn": "Y",
        "opt_type": 2,
        "prop1_cd": "001",
        "prop_val1": "속성값1",
        "prop_val2": "속성값2",
        "prop_val3": "속성값3",
        "prop_val4": "속성값4",
        "prop_val5": "속성값5",
        "prop_val6": "속성값6",
        "prop_val7": "속성값7",
        "prop_val8": "속성값8",
        "prop_val9": "속성값9",
        "prop_val10": "속성값10",
        "prop_val11": "속성값11",
        "prop_val12": "속성값12",
        "prop_val13": "속성값13",
        "prop_val14": "속성값14",
        "prop_val15": "속성값15",
        "prop_val16": "속성값16",
        "prop_val17": "속성값17",
        "prop_val18": "속성값18",
        "prop_val19": "속성값19",
        "prop_val20": "속성값20",
        "prop_val21": "속성값21",
        "prop_val22": "속성값22",
        "prop_val23": "속성값23",
        "prop_val24": "속성값24",
        "prop_val25": "속성값25",
        "prop_val26": "속성값26",
        "prop_val27": "속성값27",
        "prop_val28": "속성값28",
        "prop_val29": "속성값29",
        "prop_val30": "속성값30",
        "prop_val31": "속성값31",
        "prop_val32": "속성값32",
        "prop_val33": "속성값33",
        "pack_code_str": "PACK001,PACK002,PACK003",
        "goods_nm_en": "Test Product Name",
        "goods_nm_pr": "테스트 상품 프로모션명",
        "goods_remarks2": "테스트 상품 설명2",
        "goods_remarks3": "테스트 상품 설명3",
        "goods_remarks4": "테스트 상품 설명4",
        "importno": "IMP20240001",
        "origin2": "한국",
        "expire_dm": "20241231",
        "supply_save_yn": "Y",
        "descrition": "테스트 상품 상세 설명",
        "product_nm": "테스트 상품",
        "no_product": 1,
        "detail_img_url": "https://example.com/detail-image.jpg",
        "no_word": 10,
        "no_keyword": 5,
        "product_id": 1001
    }


@pytest.fixture
def sample_order_data() -> dict:
    """샘플 주문 데이터 (ReceiveOrder 모델 기반)"""

    return {
        "receive_dt": "2024-01-01T12:00:00",
        "idx": "TEST_ORDER_001",
        "order_id": "ORDER_20240101_001",
        "mall_id": "TEST_MALL",
        "mall_user_id": "test_user_001",
        "mall_user_id2": "test_user_001_sub",
        "order_status": "주문접수",
        "user_id": "test_user_001",
        "user_name": "테스트 주문자",
        "user_tel": "02-1234-5678",
        "user_cel": "010-1234-5678",
        "user_email": "testuser@example.com",
        "receive_name": "테스트 수취인",
        "receive_tel": "02-8765-4321",
        "receive_cel": "010-8765-4321",
        "receive_email": "receiver@example.com",
        "receive_zipcode": "12345",
        "receive_addr": "서울특별시 강남구 테스트로 123 테스트빌딩 456호",
        "delv_msg": "문앞에 놓아주세요",
        "delv_msg1": "배송 전 연락 부탁드립니다",
        "mul_delv_msg": "복수배송 메시지",
        "etc_msg": "깨지기 쉬운 상품이니 조심히 배송해주세요",
        "total_cost": 25000,
        "pay_cost": 25000,
        "sale_cost": 22000,
        "mall_won_cost": 0,
        "won_cost": 0,
        "delv_cost": 3000,
        "order_date": "2024-01-01",
        "reg_date": "20240101120000",
        "ord_confirm_date": "20240101130000",
        "rtn_dt": "20240105120000",
        "chng_dt": "20240102120000",
        "delivery_confirm_date": "20240104120000",
        "cancel_dt": None,
        "hope_delv_date": "20240103000000",
        "inv_send_dm": "20240102000000",
        "partner_id": "PARTNER_001",
        "dpartner_id": "DPARTNER_001",
        "mall_product_id": "MALL_PROD_001",
        "product_id": "PROD_001",
        "sku_id": "SKU_001",
        "p_product_name": "테스트 상품(원본)",
        "p_sku_value": "색상:빨강,사이즈:M",
        "product_name": "테스트 상품",
        "sku_value": "빨강/M",
        "compayny_goods_cd": "TEST_GOODS_001",
        "sku_alias": "TEST-RED-M",
        "goods_nm_pr": "테스트 상품 프로모션명",
        "goods_keyword": "테스트, 상품, 키워드",
        "model_no": "TEST-MODEL-001",
        "model_name": "테스트 모델",
        "barcode": "1234567890123",
        "sale_cnt": 2,
        "box_ea": 1,
        "p_ea": 2,
        "delivery_method_str": "택배",
        "delivery_method_str2": "일반택배",
        "order_gubun": "일반",
        "set_gubun": "단품",
        "jung_chk_yn": "N",
        "mall_order_seq": "1",
        "mall_order_id": "MALL_ORDER_001",
        "etc_field3": "기타 필드 정보",
        "ord_field2": "일반",
        "copy_idx": "COPY_TEST_001",
        "class_cd1": "TEST_CLASS_1",
        "class_cd2": "TEST_CLASS_2",
        "class_cd3": "TEST_CLASS_3",
        "class_cd4": "TEST_CLASS_4",
        "brand_nm": "테스트브랜드",
        "delivery_id": "DELIVERY_001",
        "invoice_no": "1234567890",
        "inv_send_msg": "송장번호 발송 완료",
        "free_gift": "테스트 사은품",
        "fld_dsp": "필드 표시 정보",
        "acnt_regs_srno": 12345,
        "order_etc_1": "확장 필드 1",
        "order_etc_2": "확장 필드 2",
        "order_etc_3": "확장 필드 3",
        "order_etc_4": "확장 필드 4",
        "order_etc_5": "확장 필드 5",
        "order_etc_6": "확장 필드 6",
        "order_etc_7": "확장 필드 7",
        "order_etc_8": "확장 필드 8",
        "order_etc_9": "확장 필드 9",
        "order_etc_10": "확장 필드 10",
        "order_etc_11": "확장 필드 11",
        "order_etc_12": "확장 필드 12",
        "order_etc_13": "확장 필드 13",
        "order_etc_14": "확장 필드 14"
    }


@pytest.fixture
def mock_external_api() -> MagicMock:
    """외부 API 모킹"""

    mock_api = MagicMock()
    mock_api.get = AsyncMock(return_value={"status": "success", "data": {}})
    mock_api.post = AsyncMock(return_value={"status": "success", "data": {}})
    mock_api.put = AsyncMock(return_value={"status": "success", "data": {}})
    mock_api.delete = AsyncMock(return_value={"status": "success", "data": {}})
    return mock_api


@pytest.fixture
def mock_file_upload() -> MagicMock:
    """파일 업로드 모킹"""
    
    mock_file = MagicMock()
    mock_file.filename = "test_file.xlsx"
    mock_file.content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    mock_file.file = BytesIO(b"test file content")
    mock_file.read = AsyncMock(return_value=b"test file content")
    return mock_file


# 테스트 마커 설정
def pytest_configure(config: pytest.Config):
    """pytest 설정"""
    
    config.addinivalue_line(
        "markers", "unit: 단위 테스트"
    )
    config.addinivalue_line(
        "markers", "integration: 통합 테스트"
    )
    config.addinivalue_line(
        "markers", "api: API 테스트"
    )
    config.addinivalue_line(
        "markers", "slow: 느린 테스트"
    )
    config.addinivalue_line(
        "markers", "db: 데이터베이스 관련 테스트"
    )
    config.addinivalue_line(
        "markers", "external: 외부 서비스 의존 테스트"
    ) 