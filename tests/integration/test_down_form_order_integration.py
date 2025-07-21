from fastapi.testclient import TestClient
from utils.logs.sabangnet_logger import get_logger


pytest_plugins = ["tests.fixtures.down_form_order.conftest"]


logger = get_logger(__name__)


class TestDownFormOrderIntegration:
    """Down Form Order 엔드포인트 통합 테스트"""

    def test_get_down_form_orders_success(
            self,
            client: TestClient,
            mock_down_form_order_read_service,
            sample_down_form_order_list
        ):
        """다운폼 주문 목록 조회 성공 테스트"""

        limit = 10

        # Mock DownFormOrderReadService
        mock_down_form_order_read_service.get_down_form_orders.return_value = sample_down_form_order_list[:limit]
            
        # When: API 요청 실행
        response = client.get(f"/api/v1/down-form-orders?skip=0&limit={limit}")
        
        # Then: 응답 검증
        assert response.status_code == 200
        response_data = response.json()
        
        # 응답 구조 검증
        assert "items" in response_data
        
        # Mock 데이터와 일치하는지 확인
        assert len(response_data["items"]) == limit

        items = response_data["items"]
        
        # 각 주문 데이터 검증
        for i, item in enumerate(items):
            sample_down_form_order = sample_down_form_order_list[i]
            assert item["content"]["id"] == sample_down_form_order["id"]
            assert item["content"]["form_name"] == sample_down_form_order["form_name"]
            assert item["content"]["order_id"] == sample_down_form_order["order_id"]
            assert item["content"]["product_name"] == sample_down_form_order["product_name"]
            assert item["content"]["sale_cnt"] == sample_down_form_order["sale_cnt"]
            assert float(item["content"]["pay_cost"]) == float(sample_down_form_order["pay_cost"])
            assert float(item["content"]["total_cost"]) == float(sample_down_form_order["total_cost"])
            assert item["status"] == "success"
            assert item["message"] is None
        
        # Mock 메서드가 올바른 파라미터로 호출되었는지 확인
        mock_down_form_order_read_service.get_down_form_orders.assert_called_once_with(skip=0, limit=limit)

    def test_get_down_form_orders_pagination_success(self, client: TestClient, mock_down_form_order_read_service, sample_down_form_order_list):
        """다운폼 주문 페이징 조회 성공 테스트"""
        # Mock DownFormOrderReadService
        mock_down_form_order_read_service.get_down_form_orders_by_pagenation.return_value = (
            sample_down_form_order_list[10:],
            4
        )
            
        # When: API 요청 실행
        response = client.get("/api/v1/down-form-orders/pagination?page=2&page_size=10")
        
        # Then: 응답 검증
        assert response.status_code == 200
        response_data = response.json()
        
        # 응답 구조 검증
        assert "total" in response_data
        assert "page" in response_data
        assert "page_size" in response_data
        assert "items" in response_data
        
        # Mock 데이터와 일치하는지 확인
        assert response_data["total"] == 4
        assert response_data["page"] == 2
        assert response_data["page_size"] == 10
        assert len(response_data["items"]) == 4
        
        items = response_data["items"]

        # 주문 데이터 검증
        for i, item in enumerate(items):
            sample_down_form_order = sample_down_form_order_list[10 + i]
            assert item["content"]["id"] == sample_down_form_order["id"]
            assert item["content"]["form_name"] == sample_down_form_order["form_name"]
            assert item["content"]["order_id"] == sample_down_form_order["order_id"]
            assert item["content"]["product_name"] == sample_down_form_order["product_name"]
            assert item["content"]["sale_cnt"] == sample_down_form_order["sale_cnt"]
            assert float(item["content"]["pay_cost"]) == float(sample_down_form_order["pay_cost"])
            assert float(item["content"]["total_cost"]) == float(sample_down_form_order["total_cost"])
            assert item["status"] == "success"
            assert item["message"] == "success"
        
        # Mock 메서드가 올바른 파라미터로 호출되었는지 확인
        mock_down_form_order_read_service.get_down_form_orders_by_pagenation.assert_called_once_with(2, 10, None)

    def test_get_down_form_orders_pagination_success_with_template_code(
            self,
            client: TestClient,
            mock_down_form_order_read_service,
            sample_down_form_order_list
        ):
        """다운폼 주문 페이징 + 템플릿 코드 조회 성공 테스트"""
        # Mock DownFormOrderReadService
        template_code = "지마켓같은것"
        target_list = []

        for sample_down_form_order in sample_down_form_order_list:
            if sample_down_form_order["form_name"] == template_code:
                target_list.append(sample_down_form_order)

        mock_down_form_order_read_service.get_down_form_orders_by_pagenation.return_value = (
            target_list,
            len(target_list)
        )
        
        # When: API 요청 실행
        response = client.get(f"/api/v1/down-form-orders/pagination?page=1&page_size=20&template_code={template_code}")
        
        # Then: 응답 검증
        assert response.status_code == 200
        response_data = response.json()
        
        # 응답 구조 검증
        assert "total" in response_data
        assert "page" in response_data
        assert "page_size" in response_data
        assert "items" in response_data
        
        # Mock 데이터와 일치하는지 확인
        assert response_data["total"] == 1
        assert response_data["page"] == 1
        assert response_data["page_size"] == 20
        assert len(response_data["items"]) == 1

        items = response_data["items"]
        
        # 주문 데이터 검증
        for i, item in enumerate(items):
            sample_down_form_order = sample_down_form_order_list[i]
            assert item["content"]["id"] == sample_down_form_order["id"]
            assert item["content"]["form_name"] == sample_down_form_order["form_name"]
            assert item["content"]["order_id"] == sample_down_form_order["order_id"]
            assert item["content"]["product_name"] == sample_down_form_order["product_name"]
            assert item["content"]["sale_cnt"] == sample_down_form_order["sale_cnt"]
            assert float(item["content"]["pay_cost"]) == float(sample_down_form_order["pay_cost"])
            assert float(item["content"]["total_cost"]) == float(sample_down_form_order["total_cost"])
            assert item["status"] == "success"
            assert item["message"] == "success"
        
        # Mock 메서드가 올바른 파라미터로 호출되었는지 확인
        mock_down_form_order_read_service.get_down_form_orders_by_pagenation.assert_called_once_with(1, 20, template_code)

    def test_bulk_create_down_form_orders_success(
            self,
            client: TestClient,
            mock_down_form_order_create_service,
            sample_down_form_order_request_data
        ):
        """다운폼 주문 대량 생성 성공 테스트"""
        # Mock DownFormOrderCreateService
        mock_down_form_order_create_service.bulk_create_down_form_orders.return_value = 2
        
        # When: API 요청 실행
        response = client.post("/api/v1/down-form-orders/bulk", json=sample_down_form_order_request_data)
        
        # Then: 응답 검증
        assert response.status_code == 200
        response_data = response.json()
        
        # 응답 구조 검증
        assert "items" in response_data
        
        # Mock 데이터와 일치하는지 확인
        assert len(response_data["items"]) == 2

        items = response_data["items"]
        
        # 각 주문 데이터 검증
        for i, item in enumerate(items):
            request_item = sample_down_form_order_request_data["items"][i]
            assert item["content"]["form_name"] == request_item["form_name"]
            assert item["content"]["order_id"] == request_item["order_id"]
            assert item["content"]["product_name"] == request_item["product_name"]
            assert item["content"]["sale_cnt"] == request_item["sale_cnt"]
            assert float(item["content"]["pay_cost"]) == request_item["pay_cost"]
            assert float(item["content"]["total_cost"]) == request_item["total_cost"]
            assert item["status"] == "success"
            assert item["message"] == "success"
        
        # Mock 메서드가 올바른 파라미터로 호출되었는지 확인
        mock_down_form_order_create_service.bulk_create_down_form_orders.assert_called_once()

    def test_bulk_update_down_form_orders_success(
            self,
            client: TestClient,
            mock_down_form_order_update_service,
            sample_down_form_order_update_request_data
        ):
        """다운폼 주문 대량 수정 성공 테스트"""

        # Mock DownFormOrderUpdateService
        mock_down_form_order_update_service.bulk_update_down_form_orders.return_value = 2
        
        # When: API 요청 실행
        response = client.put("/api/v1/down-form-orders/bulk", json=sample_down_form_order_update_request_data)
        
        # Then: 응답 검증
        assert response.status_code == 200
        response_data = response.json()
        
        # 응답 구조 검증
        assert "items" in response_data
        
        # Mock 데이터와 일치하는지 확인
        assert len(response_data["items"]) == 2

        items = response_data["items"]
        
        # 각 주문 데이터 검증
        for i, item in enumerate(items):
            request_item = sample_down_form_order_update_request_data["items"][i]
            assert item["content"]["id"] == request_item["id"]
            assert item["content"]["form_name"] == request_item["form_name"]
            assert item["content"]["order_id"] == request_item["order_id"]
            assert item["content"]["product_name"] == request_item["product_name"]
            assert item["content"]["sale_cnt"] == request_item["sale_cnt"]
            assert float(item["content"]["pay_cost"]) == request_item["pay_cost"]
            assert float(item["content"]["total_cost"]) == request_item["total_cost"]
            assert item["status"] == "success"
            assert item["message"] == "success"
        
        # Mock 메서드가 올바른 파라미터로 호출되었는지 확인
        mock_down_form_order_update_service.bulk_update_down_form_orders.assert_called_once()

    def test_bulk_delete_down_form_orders_success(
            self,
            client: TestClient,
            mock_down_form_order_delete_service,
            sample_down_form_order_delete_request_data
        ):
        """다운폼 주문 대량 삭제 성공 테스트"""
        
        mock_down_form_order_delete_service.bulk_delete_down_form_orders.return_value = 2
        
        # When: API 요청 실행
        response = client.request("DELETE", "/api/v1/down-form-orders/bulk", json=sample_down_form_order_delete_request_data)
        
        # Then: 응답 검증
        assert response.status_code == 200
        response_data = response.json()
        
        # 응답 구조 검증
        assert "items" in response_data
        assert len(response_data["items"]) == 3
        
        items = response_data["items"]

        # 각 삭제 결과 검증
        for item in items:
            assert item["content"] is None
            assert item["status"] == "success"
            assert item["message"] == "success"
        
        # Mock 메서드가 올바른 파라미터로 호출되었는지 확인
        mock_down_form_order_delete_service.bulk_delete_down_form_orders.assert_called_once_with([1, 2, 3])

    def test_delete_all_down_form_orders_success(
            self,
            client: TestClient,
            mock_down_form_order_delete_service
        ):
        """다운폼 주문 전체 삭제 성공 테스트"""
        mock_down_form_order_delete_service.delete_all_down_form_orders.return_value = 10
        
        # When: API 요청 실행
        response = client.delete("/api/v1/down-form-orders/all")
        
        # Then: 응답 검증
        assert response.status_code == 200
        response_data = response.json()
        
        # 응답 구조 검증
        assert "message" in response_data
        assert response_data["message"] == "모든 데이터 삭제 완료"
        
        # Mock 메서드가 호출되었는지 확인
        mock_down_form_order_delete_service.delete_all_down_form_orders.assert_called_once()

    def test_delete_duplicate_down_form_orders_success(self, client: TestClient, mock_down_form_order_delete_service):
        """다운폼 주문 중복 삭제 성공 테스트"""
        
        mock_down_form_order_delete_service.delete_duplicate_down_form_orders.return_value = 5
        
        # When: API 요청 실행
        response = client.delete("/api/v1/down-form-orders/duplicate")
        
        # Then: 응답 검증
        assert response.status_code == 200
        response_data = response.json()
        
        # 응답 구조 검증
        assert "message" in response_data
        assert response_data["message"] == "중복 데이터 삭제 완료: 5개 행 삭제됨"
        
        # Mock 메서드가 호출되었는지 확인
        mock_down_form_order_delete_service.delete_duplicate_down_form_orders.assert_called_once()

    def test_upload_excel_file_and_get_url_success(
            self,
            client: TestClient,
            sample_excel_file_content
        ):
        """Excel 파일 업로드 및 URL 반환 성공 테스트"""
        # Given: Excel 파일 데이터
        excel_content = sample_excel_file_content
        
        # When: API 요청 실행
        response = client.post(
            "/api/v1/down-form-orders/excel-to-minio",
            data={
                "template_code": "TEST_TEMPLATE"
            },
            files={
                "file": (
                    "test.xlsx",
                    excel_content,
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            }
        )
        
        # Then: 응답 검증
        assert response.status_code == 200
        response_data = response.json()
        
        # 응답 구조 검증
        assert "file_url" in response_data
        assert "object_name" in response_data
        assert "template_code" in response_data

    def test_get_excel_to_db_success(
            self,
            client: TestClient,
            mock_excel_handler,
            mock_data_processing_usecase,
            sample_excel_file_content
        ):
        """Excel 파일을 DB로 변환 성공 테스트"""

        # Mock DataProcessingUsecase
        expected_saved_count = 5
        mock_data_processing_usecase.process_excel_to_down_form_orders.return_value = expected_saved_count

        # Mock ExcelHandler.from_upload_file_to_dataframe
        mock_excel_handler.from_upload_file_to_dataframe.return_value = sample_excel_file_content

        # Given: Excel 파일 데이터
        excel_content = sample_excel_file_content
        
        # When: API 요청 실행
        response = client.post(
            "/api/v1/down-form-orders/excel-to-db",
            data={
                "template_code": "TEST_TEMPLATE"
            },
            files={
                "file": (
                    "test.xlsx",
                    excel_content,
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            }
        )
        
        # Then: 응답 검증
        assert response.status_code == 200
        response_data = response.json()
        
        # 응답 구조 검증
        assert "saved_count" in response_data
        assert response_data["saved_count"] == expected_saved_count
        
        # Mock 메서드가 올바른 파라미터로 호출되었는지 확인
        mock_data_processing_usecase.process_excel_to_down_form_orders.assert_called_once()
        
        # 호출된 파라미터 검증
        call_args = mock_data_processing_usecase.process_excel_to_down_form_orders.call_args
        assert call_args is not None
        assert len(call_args[0]) == 2  # dataframe, template_code
        assert call_args[0][1] == "TEST_TEMPLATE"  # template_code 검증

    def test_get_excel_to_db_without_file(self, client: TestClient):
        """Excel 파일 없이 요청 시 실패 테스트"""
        # When: 파일 없이 API 요청 실행
        response = client.post(
            "/api/v1/down-form-orders/excel-to-db",
            data={
                "template_code": "TEST_TEMPLATE"
            }
        )
        
        # Then: 응답 검증
        assert response.status_code == 422  # Validation Error

    def test_get_excel_to_db_without_template_code(self, client: TestClient, sample_excel_file_content):
        """template_code 없이 요청 시 실패 테스트"""
        # Given: Excel 파일 데이터
        excel_content = sample_excel_file_content
        
        # When: template_code 없이 API 요청 실행
        response = client.post(
            "/api/v1/down-form-orders/excel-to-db",
            files={
                "file": (
                    "test.xlsx",
                    excel_content,
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            }
        )
        
        # Then: 응답 검증
        assert response.status_code == 422  # Validation Error

    def test_get_excel_to_db_processing_error(
            self,
            client: TestClient,
            mock_data_processing_usecase,
            mock_excel_handler,
            sample_excel_file_content
        ):
        """Excel 처리 중 에러 발생 시 테스트"""
        # Mock DataProcessingUsecase에서 예외 발생
        mock_data_processing_usecase.process_excel_to_down_form_orders.side_effect = Exception("Excel 처리 중 오류 발생")
        
        # Mock ExcelHandler.from_upload_file_to_dataframe
        mock_excel_handler.from_upload_file_to_dataframe.return_value = sample_excel_file_content
        
        # Given: Excel 파일 데이터
        excel_content = sample_excel_file_content
        
        # When: API 요청 실행
        response = client.post(
            "/api/v1/down-form-orders/excel-to-db",
            data={
                "template_code": "TEST_TEMPLATE"
            },
            files={
                "file": (
                    "test.xlsx",
                    excel_content,
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            }
        )
        
        # Then: 응답 검증
        assert response.status_code == 500  # Internal Server Error
        
        # Mock 메서드가 호출되었는지 확인
        mock_data_processing_usecase.process_excel_to_down_form_orders.assert_called_once()

    def test_get_excel_to_db_invalid_file_format(self, client: TestClient):
        """잘못된 파일 형식으로 요청 시 테스트"""
        
        # Given: 잘못된 파일 데이터
        invalid_content = b"This is not an Excel file"
        
        # When: 잘못된 파일로 API 요청 실행
        response = client.post(
            "/api/v1/down-form-orders/excel-to-db",
            data={
                "template_code": "TEST_TEMPLATE"
            },
            files={
                "file": (
                    "test.txt",
                    invalid_content,
                    "text/plain"
                )
            }
        )
        
        # Then: 응답 검증 (ExcelHandler에서 처리하는 방식에 따라 다를 수 있음)
        # 일반적으로 422 또는 500 에러가 발생할 것으로 예상
        assert response.status_code in [422, 500]
