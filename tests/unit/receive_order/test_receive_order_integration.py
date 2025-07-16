import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
from tests.mock_db.mock_tables.receive_orders import RECEIVE_ORDERS
from services.receive_orders.receive_order_read_service import ReceiveOrderReadService
from services.receive_orders.receive_order_create_service import ReceiveOrderCreateService


class TestReceiveOrderIntegration:
    """receive_order 엔드포인트 통합 테스트"""
    
    @pytest.fixture
    def mock_read_service(self):
        """ReceiveOrderReadService 모킹"""
        with patch('api.v1.endpoints.receive_order.ReceiveOrderReadService') as mock:
            service_instance = AsyncMock()
            mock.return_value = service_instance
            yield service_instance
    
    @pytest.fixture
    def mock_create_service(self):
        """ReceiveOrderCreateService 모킹"""
        with patch('api.v1.endpoints.receive_order.ReceiveOrderCreateService') as mock:
            service_instance = MagicMock()
            mock.return_value = service_instance
            yield service_instance
    
    def test_get_receive_orders_all_success(self, client: TestClient, mock_read_service: AsyncMock):
        """전체 주문 조회 성공 테스트"""
        # Given: mock DB 데이터 사용
        mock_orders = RECEIVE_ORDERS[:2]  # 첫 두 개 주문 데이터
        
        expected_response = {
            "orders": [
                {
                    "idx": order["idx"],
                    "order_id": order["order_id"],
                    "mall_id": order["mall_id"],
                    "order_status": order["order_status"],
                    "user_name": order["user_name"],
                    "total_cost": float(order["total_cost"]),
                    "order_date": order["order_date"].isoformat()
                }
                for order in mock_orders
            ],
            "total_count": len(mock_orders)
        }
        
        # Mock service의 반환값 설정
        mock_read_service.get_orders.return_value = expected_response
        
        # When: API 요청 실행
        response = client.get("/api/v1/receive-order/all?skip=0&limit=2")
        
        # Then: 응답 검증
        assert response.status_code == 200
        response_data = response.json()
        
        # Mock DB 데이터와 일치하는지 확인
        assert len(response_data["orders"]) == len(mock_orders)
        for i, order in enumerate(response_data["orders"]):
            mock_order = mock_orders[i]
            assert order["idx"] == mock_order["idx"]
            assert order["order_id"] == mock_order["order_id"]
            assert order["mall_id"] == mock_order["mall_id"]
            assert order["order_status"] == mock_order["order_status"]
            assert order["user_name"] == mock_order["user_name"]
            assert order["total_cost"] == float(mock_order["total_cost"])
        
        # Mock이 올바른 파라미터로 호출되었는지 확인
        mock_read_service.get_orders.assert_called_once_with(0, 2)
    
    def test_get_receive_orders_pagination_success(self, client: TestClient, mock_read_service: AsyncMock):
        """페이징 주문 조회 성공 테스트"""
        # Given: mock DB 데이터 사용
        mock_orders = RECEIVE_ORDERS[:1]  # 첫 번째 주문 데이터
        
        expected_response = {
            "orders": [
                {
                    "idx": mock_orders[0]["idx"],
                    "order_id": mock_orders[0]["order_id"],
                    "mall_id": mock_orders[0]["mall_id"],
                    "order_status": mock_orders[0]["order_status"],
                    "user_name": mock_orders[0]["user_name"],
                    "total_cost": float(mock_orders[0]["total_cost"]),
                    "order_date": mock_orders[0]["order_date"].isoformat()
                }
            ],
            "total_count": 1,
            "page": 1,
            "page_size": 20
        }
        
        # Mock service의 반환값 설정
        mock_read_service.get_orders_pagination.return_value = expected_response
        
        # When: API 요청 실행
        response = client.get("/api/v1/receive-order/pagination?page=1&page_size=20")
        
        # Then: 응답 검증
        assert response.status_code == 200
        response_data = response.json()
        
        # Mock DB 데이터와 일치하는지 확인
        assert len(response_data["orders"]) == 1
        order = response_data["orders"][0]
        mock_order = mock_orders[0]
        assert order["idx"] == mock_order["idx"]
        assert order["order_id"] == mock_order["order_id"]
        assert order["mall_id"] == mock_order["mall_id"]
        assert order["order_status"] == mock_order["order_status"]
        assert order["user_name"] == mock_order["user_name"]
        assert order["total_cost"] == float(mock_order["total_cost"])
        
        # Mock이 올바른 파라미터로 호출되었는지 확인
        mock_read_service.get_orders_pagination.assert_called_once_with(1, 20)
    
    def test_get_receive_order_by_idx_success(self, client: TestClient, mock_read_service: AsyncMock):
        """단건 주문 조회 성공 테스트"""
        # Given: mock DB 데이터 사용
        mock_order = RECEIVE_ORDERS[0]  # 첫 번째 주문 데이터
        
        expected_response = {
            "idx": mock_order["idx"],
            "order_id": mock_order["order_id"],
            "mall_id": mock_order["mall_id"],
            "order_status": mock_order["order_status"],
            "user_name": mock_order["user_name"],
            "user_tel": mock_order["user_tel"],
            "user_cel": mock_order["user_cel"],
            "user_email": mock_order["user_email"],
            "receive_name": mock_order["receive_name"],
            "receive_tel": mock_order["receive_tel"],
            "receive_cel": mock_order["receive_cel"],
            "receive_email": mock_order["receive_email"],
            "receive_zipcode": mock_order["receive_zipcode"],
            "receive_addr": mock_order["receive_addr"],
            "total_cost": float(mock_order["total_cost"]),
            "pay_cost": float(mock_order["pay_cost"]),
            "sale_cost": float(mock_order["sale_cost"]),
            "delv_cost": float(mock_order["delv_cost"]),
            "order_date": mock_order["order_date"].isoformat(),
            "product_name": mock_order["product_name"],
            "sale_cnt": mock_order["sale_cnt"]
        }
        
        # Mock service의 반환값 설정
        mock_read_service.get_order_by_idx.return_value = expected_response
        
        # When: API 요청 실행
        response = client.get(f"/api/v1/receive-order/{mock_order['idx']}")
        
        # Then: 응답 검증
        assert response.status_code == 200
        response_data = response.json()
        
        # Mock DB 데이터와 일치하는지 확인
        assert response_data["idx"] == mock_order["idx"]
        assert response_data["order_id"] == mock_order["order_id"]
        assert response_data["mall_id"] == mock_order["mall_id"]
        assert response_data["order_status"] == mock_order["order_status"]
        assert response_data["user_name"] == mock_order["user_name"]
        assert response_data["total_cost"] == float(mock_order["total_cost"])
        assert response_data["product_name"] == mock_order["product_name"]
        assert response_data["sale_cnt"] == mock_order["sale_cnt"]
        
        # Mock이 올바른 파라미터로 호출되었는지 확인
        mock_read_service.get_order_by_idx.assert_called_once_with(mock_order["idx"])
    
    def test_get_receive_order_by_idx_not_found(self, client: TestClient, mock_read_service: AsyncMock):
        """존재하지 않는 주문 조회 실패 테스트"""
        # Given: 존재하지 않는 주문 idx
        non_existent_idx = "NON_EXISTENT_ORDER"
        
        # Mock service가 None을 반환하도록 설정
        mock_read_service.get_order_by_idx.return_value = None
        
        # When: API 요청 실행
        response = client.get(f"/api/v1/receive-order/{non_existent_idx}")
        
        # Then: 에러 응답 검증
        assert response.status_code == 404
    
    def test_make_and_get_receive_order_xml_template_success(self, client: TestClient, mock_create_service: MagicMock):
        """주문 XML 템플릿 생성 성공 테스트"""
        # Given: 요청 데이터
        request_data = {
            "date_from": "2025-06-02",
            "date_to": "2025-06-06",
            "order_status": "출고완료"
        }
        
        # Mock service가 StreamingResponse를 반환하도록 설정
        from fastapi.responses import StreamingResponse
        mock_response = StreamingResponse(
            iter([b"<?xml version='1.0' encoding='UTF-8'?><orders></orders>"]),
            media_type="application/xml"
        )
        mock_create_service.get_order_xml_template.return_value = mock_response
        
        # When: API 요청 실행
        response = client.post("/api/v1/receive-order/order-xml-template", json=request_data)
        
        # Then: 응답 검증
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/xml"
        
        # Mock이 올바른 파라미터로 호출되었는지 확인
        mock_create_service.get_order_xml_template.assert_called_once_with(
            ord_st_date="20250602",
            ord_ed_date="20250606",
            order_status="출고완료"
        )
    
    def test_save_receive_orders_to_db_success(self, client: TestClient, mock_create_service: MagicMock):
        """XML에서 주문 데이터 저장 성공 테스트"""
        # Given: 요청 데이터
        request_data = {
            "date_from": "2025-06-02",
            "date_to": "2025-06-06",
            "order_status": "출고완료"
        }
        
        # Mock service 메서드들 설정
        mock_create_service.create_request_xml.return_value = "/path/to/xml/file.xml"
        mock_create_service.get_xml_url_from_minio.return_value = "http://example.com/xml"
        mock_create_service.get_orders_from_sabangnet.return_value = "<xml>test</xml>"
        mock_create_service.save_orders_to_db_from_xml.return_value = {
            "message": "주문 데이터 저장이 완료되었습니다.",
            "saved_count": 2,
            "xml_content_length": 100
        }
        
        # When: API 요청 실행
        response = client.post("/api/v1/receive-order/orders-from-xml", json=request_data)
        
        # Then: 응답 검증
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["message"] == "주문 데이터 저장이 완료되었습니다."
        assert response_data["saved_count"] == 2
        assert response_data["xml_content_length"] == 100
        
        # Mock 메서드들이 올바른 파라미터로 호출되었는지 확인
        mock_create_service.create_request_xml.assert_called_once_with(
            ord_st_date="20250602",
            ord_ed_date="20250606",
            order_status="출고완료"
        )
        mock_create_service.get_xml_url_from_minio.assert_called_once_with("/path/to/xml/file.xml")
        mock_create_service.get_orders_from_sabangnet.assert_called_once_with("http://example.com/xml")
        mock_create_service.save_orders_to_db_from_xml.assert_called_once_with("<xml>test</xml>", True)
    
    def test_get_receive_orders_all_with_invalid_params(self, client: TestClient):
        """잘못된 파라미터로 전체 주문 조회 실패 테스트"""
        # Given: 잘못된 파라미터
        invalid_params = [
            {"skip": -1, "limit": 2},  # skip이 음수
            {"skip": 0, "limit": 0},   # limit이 0
            {"skip": 0, "limit": 201}  # limit이 최대값 초과
        ]
        
        for params in invalid_params:
            # When: API 요청 실행
            response = client.get("/api/v1/receive-order/all", params=params)
            
            # Then: 검증 에러 응답
            assert response.status_code == 422
    
    def test_get_receive_orders_pagination_with_invalid_params(self, client: TestClient):
        """잘못된 파라미터로 페이징 주문 조회 실패 테스트"""
        # Given: 잘못된 파라미터
        invalid_params = [
            {"page": 0, "page_size": 20},   # page가 0
            {"page": 1, "page_size": 0},    # page_size가 0
        ]
        
        for params in invalid_params:
            # When: API 요청 실행
            response = client.get("/api/v1/receive-order/pagination", params=params)
            
            # Then: 검증 에러 응답
            assert response.status_code == 422
    
    def test_save_receive_orders_to_db_with_invalid_dates(self, client: TestClient):
        """잘못된 날짜로 주문 데이터 저장 실패 테스트"""
        # Given: 잘못된 날짜 범위
        invalid_request_data = {
            "date_from": "2025-06-06",  # 종료일이 시작일보다 빠름
            "date_to": "2025-06-02",
            "order_status": "출고완료"
        }
        
        # When: API 요청 실행
        response = client.post("/api/v1/receive-order/orders-from-xml", json=invalid_request_data)
        
        # Then: 검증 에러 응답
        assert response.status_code == 422
    
    def test_save_receive_orders_to_db_with_invalid_order_status(self, client: TestClient):
        """잘못된 주문 상태로 주문 데이터 저장 실패 테스트"""
        # Given: 잘못된 주문 상태
        invalid_request_data = {
            "date_from": "2025-06-02",
            "date_to": "2025-06-06",
            "order_status": "존재하지않는상태"
        }
        
        # When: API 요청 실행
        response = client.post("/api/v1/receive-order/orders-from-xml", json=invalid_request_data)
        
        # Then: 검증 에러 응답
        assert response.status_code == 422
    
    def test_get_receive_orders_with_mock_db_data_validation(self, client: TestClient, mock_read_service: AsyncMock):
        """mock DB 데이터 검증을 통한 주문 조회 테스트"""
        # Given: mock DB의 모든 주문 데이터 사용
        mock_orders = RECEIVE_ORDERS
        
        expected_response = {
            "orders": [
                {
                    "idx": order["idx"],
                    "order_id": order["order_id"],
                    "mall_id": order["mall_id"],
                    "order_status": order["order_status"],
                    "user_name": order["user_name"],
                    "total_cost": float(order["total_cost"]),
                    "order_date": order["order_date"].isoformat(),
                    "product_name": order["product_name"],
                    "sale_cnt": order["sale_cnt"]
                }
                for order in mock_orders
            ],
            "total_count": len(mock_orders)
        }
        
        # Mock service의 반환값 설정
        mock_read_service.get_orders.return_value = expected_response
        
        # When: API 요청 실행
        response = client.get(f"/api/v1/receive-order/all?skip=0&limit={len(mock_orders)}")
        
        # Then: 응답 검증
        assert response.status_code == 200
        response_data = response.json()
        
        # Mock DB 데이터와 일치하는지 확인
        assert len(response_data["orders"]) == len(mock_orders)
        for i, order in enumerate(response_data["orders"]):
            mock_order = mock_orders[i]
            assert order["idx"] == mock_order["idx"]
            assert order["order_id"] == mock_order["order_id"]
            assert order["mall_id"] == mock_order["mall_id"]
            assert order["order_status"] == mock_order["order_status"]
            assert order["user_name"] == mock_order["user_name"]
            assert order["total_cost"] == float(mock_order["total_cost"])
            assert order["product_name"] == mock_order["product_name"]
            assert order["sale_cnt"] == mock_order["sale_cnt"] 