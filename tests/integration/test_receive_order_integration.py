from decimal import Decimal
from fastapi.testclient import TestClient
from fastapi.responses import StreamingResponse
from schemas.receive_orders.receive_orders_dto import ReceiveOrdersDto
from schemas.receive_orders.response.receive_orders_response import ReceiveOrdersBulkCreateResponse


pytest_plugins = ["tests.fixtures.receive_order.conftest"]


class TestReceiveOrderIntegration:
    """Receive Order 엔드포인트 통합 테스트"""

    def test_get_receive_orders_all_success(
            self,
            client: TestClient,
            mock_receive_order_read_service
        ):
        """주문 수집 데이터 전체 조회 성공 테스트"""
        
        # Mock ReceiveOrderReadService
        mock_service = mock_receive_order_read_service
            
        # Mock get_orders 메서드
        mock_orders = [
            ReceiveOrdersDto(
                idx="TEST_ORDER_001",
                mall_id="TEST_MALL",
                user_name="테스트 주문자",
                receive_name="테스트 수취인",
                total_cost=Decimal("25000"),
                order_date="20250602",
                created_at=None,
                updated_at=None
            ),
            ReceiveOrdersDto(
                idx="TEST_ORDER_002",
                mall_id="TEST_MALL",
                user_name="테스트 주문자2",
                receive_name="테스트 수취인2",
                total_cost=Decimal("30000"),
                order_date="20250602",
                created_at=None,
                updated_at=None
            )
        ]
        
        # ReceiveOrdersBulkDto 생성
        from schemas.receive_orders.receive_orders_dto import ReceiveOrdersBulkDto
        mock_bulk_dto = ReceiveOrdersBulkDto(
            success_count=2,
            error_count=0,
            success_idx=["TEST_ORDER_001", "TEST_ORDER_002"],
            errors=[],
            success_data=mock_orders
        )
        
        mock_service.get_orders.return_value = mock_bulk_dto
        
        # When: API 요청 실행
        response = client.get("/api/v1/receive-orders/all?skip=0&limit=3")
        
        # Then: 응답 검증
        assert response.status_code == 200
        response_data = response.json()
        
        # 응답 구조 검증
        assert "success_data" in response_data
        assert "success_count" in response_data
        assert "error_count" in response_data
        
        # Mock 데이터와 일치하는지 확인
        assert len(response_data["success_data"]) == 2
        assert response_data["success_count"] == 2
        assert response_data["error_count"] == 0
        
        # 각 주문 데이터 검증
        for i, order_response in enumerate(response_data["success_data"]):
            order_data = order_response["receive_orders_dto"]
            mock_order = mock_orders[i]
            assert order_data["idx"] == mock_order.idx
            assert order_data["mall_id"] == mock_order.mall_id
            assert order_data["user_name"] == mock_order.user_name
            assert order_data["receive_name"] == mock_order.receive_name
            assert float(order_data["total_cost"]) == float(mock_order.total_cost)
            assert order_data["order_date"] == mock_order.order_date.isoformat().replace('+00:00', '') + "Z"
        
        # Mock 메서드가 올바른 파라미터로 호출되었는지 확인
        mock_service.get_orders.assert_called_once_with(0, 3)

    def test_get_receive_orders_pagination_success(
            self,
            client: TestClient,
            mock_receive_order_read_service
        ):
        """주문 수집 데이터 페이징 조회 성공 테스트"""

        # Mock ReceiveOrderReadService
        mock_service = mock_receive_order_read_service
            
        # Mock get_orders_pagination 메서드
        mock_orders = [
            ReceiveOrdersDto(
                idx="TEST_ORDER_001",
                mall_id="TEST_MALL",
                user_name="테스트 주문자",
                receive_name="테스트 수취인",
                total_cost=Decimal("25000"),
                order_date="20250602",
                created_at=None,
                updated_at=None
            )
        ]
        
        # ReceiveOrdersBulkDto 생성
        from schemas.receive_orders.receive_orders_dto import ReceiveOrdersBulkDto
        mock_bulk_dto = ReceiveOrdersBulkDto(
            success_count=1,
            error_count=0,
            success_idx=["TEST_ORDER_001"],
            errors=[],
            success_data=mock_orders
        )
        
        mock_service.get_orders_pagination.return_value = mock_bulk_dto
        
        # When: API 요청 실행
        response = client.get("/api/v1/receive-orders/pagination?page=1&page_size=20")
        
        # Then: 응답 검증
        assert response.status_code == 200
        response_data = response.json()
        
        # 응답 구조 검증
        assert "success_data" in response_data
        assert "success_count" in response_data
        assert "error_count" in response_data
        
        # Mock 데이터와 일치하는지 확인
        assert len(response_data["success_data"]) == 1
        assert response_data["success_count"] == 1
        assert response_data["error_count"] == 0
        
        # 주문 데이터 검증
        order_response = response_data["success_data"][0]
        order_data = order_response["receive_orders_dto"]
        mock_order = mock_orders[0]
        assert order_data["idx"] == mock_order.idx
        assert order_data["mall_id"] == mock_order.mall_id
        assert order_data["user_name"] == mock_order.user_name
        assert order_data["receive_name"] == mock_order.receive_name
        assert float(order_data["total_cost"]) == float(mock_order.total_cost)
        assert order_data["order_date"] == mock_order.order_date.isoformat().replace('+00:00', '') + "Z"
        
        # Mock 메서드가 올바른 파라미터로 호출되었는지 확인
        mock_service.get_orders_pagination.assert_called_once_with(1, 20)

    def test_get_receive_order_by_idx_success(
            self,
            client: TestClient,
            mock_receive_order_read_service
        ):
        """주문 수집 데이터 단건 조회 성공 테스트"""
        
        # Mock ReceiveOrderReadService
        mock_service = mock_receive_order_read_service
            
        # Mock get_order_by_idx 메서드
        mock_order = ReceiveOrdersDto(
            idx="TEST_ORDER_001",
            mall_id="TEST_MALL",
            user_name="테스트 주문자",
            receive_name="테스트 수취인",
            total_cost=Decimal("25000"),
            order_date="20250602",
            created_at=None,
            updated_at=None
        )
        
        mock_service.get_order_by_idx.return_value = mock_order
        
        # When: API 요청 실행
        response = client.get("/api/v1/receive-orders/TEST_ORDER_001")
        
        # Then: 응답 검증
        assert response.status_code == 200
        response_data = response.json()
        
        # 응답 구조 검증
        assert "receive_orders_dto" in response_data
        
        # Mock 데이터와 일치하는지 확인
        order_data = response_data["receive_orders_dto"]
        assert order_data["idx"] == mock_order.idx
        assert order_data["mall_id"] == mock_order.mall_id
        assert order_data["user_name"] == mock_order.user_name
        assert order_data["receive_name"] == mock_order.receive_name
        assert order_data["total_cost"] == str(mock_order.total_cost)  # Decimal이 문자열로 변환됨
        assert order_data["order_date"] == mock_order.order_date.isoformat().replace('+00:00', '') + "Z"
        
        # Mock 메서드가 올바른 파라미터로 호출되었는지 확인
        mock_service.get_order_by_idx.assert_called_once_with("TEST_ORDER_001")

    def test_get_receive_order_by_idx_not_found(
            self,
            client: TestClient,
            mock_receive_order_read_service
        ):
        """존재하지 않는 주문 조회 실패 테스트"""
        
        # Mock ReceiveOrderReadService가 None 반환
        mock_service = mock_receive_order_read_service
            
        # Mock get_order_by_idx 메서드가 None 반환
        mock_service.get_order_by_idx.return_value = None
        
        # When: API 요청 실행
        response = client.get("/api/v1/receive-orders/NON_EXISTENT_ORDER")
        
        # Then: 404 에러 응답 검증
        assert response.status_code == 404
        response_data = response.json()
        assert response_data["detail"] == "주문을 찾을 수 없습니다."

    def test_get_receive_orders_with_invalid_pagination(
            self,
            client: TestClient,
            mock_receive_order_read_service
        ):
        """잘못된 페이징 파라미터로 주문 조회 실패 테스트"""
        
        # Mock ReceiveOrderReadService
        mock_service = mock_receive_order_read_service
        
        # Given: 잘못된 페이징 파라미터
        invalid_requests = [
            "/api/v1/receive-orders/all?skip=-1&limit=3",  # 음수 skip
            "/api/v1/receive-orders/all?skip=0&limit=0",   # 0 limit
            "/api/v1/receive-orders/all?skip=0&limit=201", # 200 초과 limit
            "/api/v1/receive-orders/pagination?page=0&page_size=20",  # 0 페이지
            "/api/v1/receive-orders/pagination?page=1&page_size=0",   # 0 page_size
        ]
        
        for url in invalid_requests:
            # When: API 요청 실행
            response = client.get(url)
            
            # Then: 검증 에러 응답
            assert response.status_code == 422

    def test_make_receive_order_xml_template_success(
            self,
            client: TestClient,
            mock_receive_order_create_service
        ):
        """주문 XML 템플릿 생성 성공 테스트"""
        
        # Mock ReceiveOrderCreateService
        mock_service = mock_receive_order_create_service
        mock_service.get_order_xml_template.return_value = StreamingResponse(
            iter([b"test xml content"]),
            media_type="application/xml",
            headers={"Content-Disposition": "attachment; filename=order_template.xml"}
        )
        
        # Given: 요청 데이터
        request_data = {
            "date_from": "2025-06-02",
            "date_to": "2025-06-06",
            "order_status": "출고완료"
        }
        
        # When: API 요청 실행
        response = client.post("/api/v1/receive-orders/xml-template", data=request_data)
        
        # Then: 응답 검증
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/xml"
        assert "attachment; filename=order_template.xml" in response.headers["content-disposition"]
        
        # Mock 메서드가 올바른 파라미터로 호출되었는지 확인
        mock_service.get_order_xml_template.assert_called_once_with(
            ord_st_date="20250602",
            ord_ed_date="20250606",
            order_status="004"
        )

    def test_make_receive_order_xml_template_with_empty_request(
            self,
            client: TestClient,
            mock_receive_order_create_service
        ):
        """요청 데이터가 없을 때 주문 XML 템플릿 생성 실패 테스트"""

        # Mock ReceiveOrderCreateService
        mock_service = mock_receive_order_create_service
            
        # Mock get_order_xml_template 메서드
        mock_streaming_response = StreamingResponse(
            iter([b"test xml content"]),
            media_type="application/xml",
            headers={"Content-Disposition": "attachment; filename=order_template.xml"}
        )
        
        mock_service.get_order_xml_template.return_value = mock_streaming_response
        
        # Given: 기본값 사용 (요청 데이터 없음)
        request_data = {}
        
        # When: API 요청 실행
        response = client.post("/api/v1/receive-orders/xml-template", data=request_data)
        
        # Then: 응답 검증
        assert response.status_code == 422

    def test_save_receive_orders_to_db_from_xml_success(
            self,
            client: TestClient,
            mock_receive_order_create_service
        ):
        """XML에서 주문 데이터 생성 성공 테스트"""

        # Mock ReceiveOrderCreateService
        mock_service = mock_receive_order_create_service

        # Mock service 메서드들 설정
        mock_service.create_request_xml.return_value = "/path/to/xml/file.xml"
        mock_service.get_xml_url_from_minio.return_value = "http://example.com/xml"
        mock_service.get_orders_from_sabangnet.return_value = """
        <SABANGNET_ORDER_INFO>
            <DATA>
                <ORDER_ID>ORDER_20250602_001</ORDER_ID>
                <MALL_ID>TEST_MALL</MALL_ID>
                <USER_NAME>테스트 주문자</USER_NAME>
                <RECEIVE_NAME>테스트 수취인</RECEIVE_NAME>
                <TOTAL_COST>25000</TOTAL_COST>
                <ORDER_DATE>20250602</ORDER_DATE>
            </DATA>
            <DATA>
                <ORDER_ID>ORDER_20250602_002</ORDER_ID>
                <MALL_ID>TEST_MALL</MALL_ID>
                <USER_NAME>테스트 주문자2</USER_NAME>
                <RECEIVE_NAME>테스트 수취인2</RECEIVE_NAME>
                <TOTAL_COST>30000</TOTAL_COST>
                <ORDER_DATE>20250602</ORDER_DATE>
            </DATA>
        </SABANGNET_ORDER_INFO>
        """
        
        # Mock DB 저장 결과
        mock_bulk_response = ReceiveOrdersBulkCreateResponse(
            total_count=2,
            success_count=2,
            duplicated_count=0
        )
        
        mock_service.save_orders_to_db_from_xml.return_value = mock_bulk_response
        
        # Given: 기본 요청 데이터
        request_data = {
            "date_from": "2025-06-02",
            "date_to": "2025-06-06",
            "order_status": "출고완료"
        }
        
        # When: API 요청 실행
        response = client.post("/api/v1/receive-orders/from-sabangnet/to-db", data=request_data)
        
        # Then: 응답 검증
        assert response.status_code == 200
        response_data = response.json()
        
        # 응답 구조 검증
        assert "total_count" in response_data
        assert "success_count" in response_data
        assert "duplicated_count" in response_data
        
        # Mock 데이터와 일치하는지 확인
        assert response_data["total_count"] == 2
        assert response_data["success_count"] == 2
        assert response_data["duplicated_count"] == 0
        
        # Mock 메서드들이 올바른 파라미터로 호출되었는지 확인
        mock_service.create_request_xml.assert_called_once_with(
            ord_st_date="20250602",
            ord_ed_date="20250606",
            order_status="004"
        )
        # get_xml_url_from_minio는 동기 메서드이므로 await 없이 호출됨
        mock_service.get_xml_url_from_minio.assert_called_once()
        mock_service.get_orders_from_sabangnet.assert_called_once()
        mock_service.save_orders_to_db_from_xml.assert_called_once()

    def test_save_receive_orders_to_db_from_xml_with_empty_request(
            self,
            client: TestClient,
            mock_receive_order_create_service
        ):
        """기본값으로 XML에서 주문 데이터 생성 테스트"""

        # Mock ReceiveOrderCreateService
        mock_service = mock_receive_order_create_service
            
        # Mock service 메서드들 설정
        mock_service.create_request_xml.return_value = "/path/to/xml/file.xml"
        mock_service.get_xml_url_from_minio.return_value = "http://example.com/xml"
        mock_service.get_orders_from_sabangnet.return_value = """
        <SABANGNET_ORDER_INFO>
            <DATA>
                <ORDER_ID>ORDER_20250602_001</ORDER_ID>
                <MALL_ID>TEST_MALL</MALL_ID>
                <USER_NAME>테스트 주문자</USER_NAME>
                <RECEIVE_NAME>테스트 수취인</RECEIVE_NAME>
                <TOTAL_COST>25000</TOTAL_COST>
                <ORDER_DATE>20250602</ORDER_DATE>
            </DATA>
        </SABANGNET_ORDER_INFO>
        """
        
        # Mock DB 저장 결과
        mock_bulk_response = ReceiveOrdersBulkCreateResponse(
            total_count=1,
            success_count=1,
            duplicated_count=0
        )
        
        mock_service.save_orders_to_db_from_xml.return_value = mock_bulk_response
        
        # Given: 기본값 사용 (요청 데이터 없음)
        request_data = {}
        
        # When: API 요청 실행
        response = client.post("/api/v1/receive-orders/from-sabangnet/to-db", data=request_data)
        
        # Then: 응답 검증
        assert response.status_code == 422

    def test_save_receive_orders_to_db_from_xml_api_error(
            self,
            client: TestClient,
            mock_receive_order_create_service
        ):
        """XML API 요청 실패 테스트"""

        # Mock ReceiveOrderCreateService가 API 요청에서 실패
        mock_service = mock_receive_order_create_service
            
        # Mock service가 API 요청에서 실패하도록 설정
        mock_service.create_request_xml.return_value = "/path/to/xml/file.xml"
        mock_service.get_xml_url_from_minio.return_value = "http://example.com/xml"
        mock_service.get_orders_from_sabangnet.side_effect = Exception("API 요청 실패")
        
        # Given: 기본 요청 데이터
        request_data = {
            "date_from": "2025-06-02",
            "date_to": "2025-06-06",
            "order_status": "출고완료"
        }
        
        # When: API 요청 실행
        response = client.post("/api/v1/receive-orders/from-sabangnet/to-db", data=request_data)
        
        # Then: 에러 응답 검증
        assert response.status_code == 500
        response_data = response.json()
        assert "API 요청 실패" in response_data["detail"]

    def test_save_receive_orders_to_db_from_xml_db_save_error(
            self,
            client: TestClient,
            mock_receive_order_create_service
        ):
        """DB 저장 실패 테스트"""

        # Mock ReceiveOrderCreateService가 DB 저장에서 실패
        mock_service = mock_receive_order_create_service
            
        # Mock service 메서드들 설정
        mock_service.create_request_xml.return_value = "/path/to/xml/file.xml"
        mock_service.get_xml_url_from_minio.return_value = "http://example.com/xml"
        mock_service.get_orders_from_sabangnet.return_value = """
        <SABANGNET_ORDER_INFO>
            <DATA>
                <ORDER_ID>ORDER_20250602_001</ORDER_ID>
                <MALL_ID>TEST_MALL</MALL_ID>
                <USER_NAME>테스트 주문자</USER_NAME>
                <RECEIVE_NAME>테스트 수취인</RECEIVE_NAME>
                <TOTAL_COST>25000</TOTAL_COST>
                <ORDER_DATE>20250602</ORDER_DATE>
            </DATA>
        </SABANGNET_ORDER_INFO>
        """
        
        # Mock DB 저장에서 실패하도록 설정
        mock_service.save_orders_to_db_from_xml.side_effect = Exception("DB 저장 실패")
        
        # Given: 기본 요청 데이터
        request_data = {
            "date_from": "2025-06-02",
            "date_to": "2025-06-06",
            "order_status": "출고완료"
        }
        
        # When: API 요청 실행
        response = client.post("/api/v1/receive-orders/from-sabangnet/to-db", data=request_data)
        
        # Then: 에러 응답 검증
        assert response.status_code == 500
        response_data = response.json()
        assert "DB 저장 실패" in response_data["detail"]

    def test_make_receive_order_xml_template_with_invalid_date_range(
            self,
            client: TestClient,
        ):
        """잘못된 날짜 범위로 XML 템플릿 생성 실패 테스트"""

        # Given: 잘못된 날짜 범위
        invalid_requests = [
            {
                "date_from": "2025-06-06",
                "date_to": "2025-06-02",  # 시작일이 종료일보다 늦음
                "order_status": "출고완료"
            }
        ]
        
        for request_data in invalid_requests:
            # When: API 요청 실행
            response = client.post("/api/v1/receive-orders/xml-template", data=request_data)
            
            # Then: 검증 에러 응답
            assert response.status_code == 422

    def test_save_receive_orders_to_db_from_xml_with_invalid_order_status(
            self,
            client: TestClient,
        ):
        """잘못된 주문 상태로 XML 요청 실패 테스트"""
        
        # Given: 잘못된 주문 상태
        request_data = {
            "date_from": "2025-06-02",
            "date_to": "2025-06-06",
            "order_status": "존재하지않는상태"
        }
        
        # When: API 요청 실행
        response = client.post("/api/v1/receive-orders/from-sabangnet/to-db", data=request_data)
        
        # Then: 검증 에러 응답
        assert response.status_code == 422
