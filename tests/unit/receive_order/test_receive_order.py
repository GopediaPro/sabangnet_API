"""
주문 수신 API 테스트
"""
import pytest

from fastapi import FastAPI
from fastapi.testclient import TestClient

from unittest.mock import AsyncMock, MagicMock
from utils.logs.sabangnet_logger import get_logger

from api.v1.endpoints.receive_order import get_receive_order_read_service
from api.v1.endpoints.receive_order import get_receive_order_create_service


logger = get_logger(__name__)


@pytest.mark.api
class TestReceiveOrderAPI:
    """주문 수신 API 테스트 클래스"""

    def test_get_receive_orders_success(self, test_app: FastAPI, async_client: TestClient):
        """주문 수신 목록 조회 성공 테스트"""
        try:
            logger.info("주문 수신 목록 조회 성공 테스트 시작")
            
            mock_orders = [
                {
                    "id": 1,
                    "order_id": "ORDER001",
                    "product_name": "테스트상품1",
                    "sale_cnt": 1,
                    "pay_cost": 12000,
                    "receive_name": "홍길동"
                },
                {
                    "id": 2,
                    "order_id": "ORDER002",
                    "product_name": "테스트상품2",
                    "sale_cnt": 2,
                    "pay_cost": 24000,
                    "receive_name": "김철수"
                }
            ]
            
            mock_service = MagicMock()
            mock_service.get_receive_orders_by_pagination = AsyncMock(return_value=mock_orders)
            
            test_app.dependency_overrides[get_receive_order_read_service] = lambda: mock_service
            
            try:
                response = async_client.get("/api/v1/receive-order/pagination?page=1")
                
                assert response.status_code == 200
                data = response.json()
                assert "receive_orders" in data
                assert "current_page" in data
                assert "page_size" in data
                assert len(data["receive_orders"]) == 2
                
            finally:
                test_app.dependency_overrides = {}
                
            logger.info("주문 수신 목록 조회 성공 테스트 완료")
        except Exception as e:
            logger.error(f"주문 수신 목록 조회 성공 테스트 실패: {e}")
            raise e

    def test_get_receive_orders_invalid_page(self, async_client: TestClient):
        """주문 수신 목록 조회 잘못된 페이지 테스트"""
        try:
            logger.info("주문 수신 목록 조회 잘못된 페이지 테스트 시작")
            
            response = async_client.get("/api/v1/receive-order/pagination?page=0")
            
            assert response.status_code == 422  # Validation Error
            
            logger.info("주문 수신 목록 조회 잘못된 페이지 테스트 완료")
        except Exception as e:
            logger.error(f"주문 수신 목록 조회 잘못된 페이지 테스트 실패: {e}")
            raise e

    def test_create_receive_order_success(self, test_app: FastAPI, async_client: TestClient):
        """주문 수신 생성 성공 테스트"""
        try:
            logger.info("주문 수신 생성 성공 테스트 시작")
            
            test_data = {
                "order_id": "ORDER001",
                "product_name": "테스트상품1",
                "sale_cnt": 1,
                "pay_cost": 12000,
                "receive_name": "홍길동",
                "receive_phone": "010-1234-5678",
                "receive_address": "서울시 강남구"
            }
            
            mock_dto = {
                "id": 1,
                "order_id": "ORDER001",
                "product_name": "테스트상품1",
                "sale_cnt": 1,
                "pay_cost": 12000,
                "receive_name": "홍길동"
            }
            
            mock_service = MagicMock()
            mock_service.create_receive_order = AsyncMock(return_value=mock_dto)
            
            test_app.dependency_overrides[get_receive_order_create_service] = lambda: mock_service
            
            try:
                response = async_client.post("/api/v1/receive-order/orders-from-xml", json=test_data)
                
                assert response.status_code == 200
                data = response.json()
                assert "id" in data
                assert data["order_id"] == "ORDER001"
                
            finally:
                test_app.dependency_overrides = {}
                
            logger.info("주문 수신 생성 성공 테스트 완료")
        except Exception as e:
            logger.error(f"주문 수신 생성 성공 테스트 실패: {e}")
            raise e

    def test_create_receive_order_invalid_request(self, async_client: TestClient):
        """주문 수신 생성 잘못된 요청 테스트"""
        try:
            logger.info("주문 수신 생성 잘못된 요청 테스트 시작")
            
            # 필수 필드가 없는 요청
            test_data = {}
            
            response = async_client.post("/api/v1/receive-order", json=test_data)
            
            assert response.status_code == 422  # Validation Error
            
            logger.info("주문 수신 생성 잘못된 요청 테스트 완료")
        except Exception as e:
            logger.error(f"주문 수신 생성 잘못된 요청 테스트 실패: {e}")
            raise e

    def test_create_receive_order_db_error(self, test_app: FastAPI, async_client: TestClient):
        """주문 수신 생성 DB 에러 테스트"""
        try:
            logger.info("주문 수신 생성 DB 에러 테스트 시작")
            
            test_data = {
                "order_id": "ORDER001",
                "product_name": "테스트상품1",
                "sale_cnt": 1,
                "pay_cost": 12000,
                "receive_name": "홍길동"
            }
            
            mock_service = MagicMock()
            mock_service.create_receive_order = AsyncMock(side_effect=Exception("DB 연결 오류"))
            
            test_app.dependency_overrides[get_receive_order_create_service] = lambda: mock_service
            
            try:
                response = async_client.post("/api/v1/receive-order", json=test_data)
                
                assert response.status_code == 500
                data = response.json()
                assert "detail" in data
                
            finally:
                test_app.dependency_overrides = {}
                
            logger.info("주문 수신 생성 DB 에러 테스트 완료")
        except Exception as e:
            logger.error(f"주문 수신 생성 DB 에러 테스트 실패: {e}")
            raise e

    def test_bulk_create_receive_orders_success(self, test_app: FastAPI, async_client: TestClient):
        """주문 수신 벌크 생성 성공 테스트"""
        try:
            logger.info("주문 수신 벌크 생성 성공 테스트 시작")
            
            test_data = {
                "items": [
                    {
                        "order_id": "ORDER001",
                        "product_name": "테스트상품1",
                        "sale_cnt": 1,
                        "pay_cost": 12000,
                        "receive_name": "홍길동"
                    },
                    {
                        "order_id": "ORDER002",
                        "product_name": "테스트상품2",
                        "sale_cnt": 2,
                        "pay_cost": 24000,
                        "receive_name": "김철수"
                    }
                ]
            }
            
            mock_dto_list = [
                {
                    "id": 1,
                    "order_id": "ORDER001",
                    "product_name": "테스트상품1",
                    "sale_cnt": 1,
                    "pay_cost": 12000,
                    "receive_name": "홍길동"
                },
                {
                    "id": 2,
                    "order_id": "ORDER002",
                    "product_name": "테스트상품2",
                    "sale_cnt": 2,
                    "pay_cost": 24000,
                    "receive_name": "김철수"
                }
            ]
            
            mock_service = MagicMock()
            mock_service.bulk_create_receive_orders = AsyncMock(return_value=mock_dto_list)
            
            test_app.dependency_overrides[get_receive_order_create_service] = lambda: mock_service
            
            try:
                response = async_client.post("/api/v1/receive-order/bulk", json=test_data)
                
                assert response.status_code == 200
                data = response.json()
                assert "items" in data
                assert len(data["items"]) == 2
                
            finally:
                test_app.dependency_overrides = {}
                
            logger.info("주문 수신 벌크 생성 성공 테스트 완료")
        except Exception as e:
            logger.error(f"주문 수신 벌크 생성 성공 테스트 실패: {e}")
            raise e

    def test_bulk_create_receive_orders_invalid_request(self, async_client: TestClient):
        """주문 수신 벌크 생성 잘못된 요청 테스트"""
        try:
            logger.info("주문 수신 벌크 생성 잘못된 요청 테스트 시작")
            
            # 필수 필드가 없는 요청
            test_data = {}
            
            response = async_client.post("/api/v1/receive-order/bulk", json=test_data)
            
            assert response.status_code == 422  # Validation Error
            
            logger.info("주문 수신 벌크 생성 잘못된 요청 테스트 완료")
        except Exception as e:
            logger.error(f"주문 수신 벌크 생성 잘못된 요청 테스트 실패: {e}")
            raise e

    def test_bulk_create_receive_orders_db_error(self, test_app: FastAPI, async_client: TestClient):
        """주문 수신 벌크 생성 DB 에러 테스트"""
        try:
            logger.info("주문 수신 벌크 생성 DB 에러 테스트 시작")
            
            test_data = {
                "items": [
                    {
                        "order_id": "ORDER001",
                        "product_name": "테스트상품1",
                        "sale_cnt": 1,
                        "pay_cost": 12000,
                        "receive_name": "홍길동"
                    }
                ]
            }
            
            mock_service = MagicMock()
            mock_service.bulk_create_receive_orders = AsyncMock(side_effect=Exception("DB 연결 오류"))
            
            test_app.dependency_overrides[get_receive_order_create_service] = lambda: mock_service
            
            try:
                response = async_client.post("/api/v1/receive-order/bulk", json=test_data)
                
                assert response.status_code == 500
                data = response.json()
                assert "detail" in data
                
            finally:
                test_app.dependency_overrides = {}
                
            logger.info("주문 수신 벌크 생성 DB 에러 테스트 완료")
        except Exception as e:
            logger.error(f"주문 수신 벌크 생성 DB 에러 테스트 실패: {e}")
            raise e

    def test_create_receive_order_validation_error(self, test_app: FastAPI, async_client: TestClient):
        """주문 수신 생성 유효성 검증 에러 테스트"""
        try:
            logger.info("주문 수신 생성 유효성 검증 에러 테스트 시작")
            
            test_data = {
                "order_id": "ORDER001",
                "product_name": "테스트상품1",
                "sale_cnt": -1,  # 잘못된 수량
                "pay_cost": 12000,
                "receive_name": "홍길동"
            }
            
            mock_service = MagicMock()
            mock_service.create_receive_order = AsyncMock(side_effect=ValueError("수량은 0보다 커야 합니다"))
            
            test_app.dependency_overrides[get_receive_order_create_service] = lambda: mock_service
            
            try:
                response = async_client.post("/api/v1/receive-order", json=test_data)
                
                assert response.status_code == 400
                data = response.json()
                assert "detail" in data
                
            finally:
                test_app.dependency_overrides = {}
                
            logger.info("주문 수신 생성 유효성 검증 에러 테스트 완료")
        except Exception as e:
            logger.error(f"주문 수신 생성 유효성 검증 에러 테스트 실패: {e}")
            raise e 