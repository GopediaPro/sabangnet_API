from decimal import Decimal
from datetime import datetime
from fastapi.testclient import TestClient
from fastapi.responses import StreamingResponse
from schemas.product.product_raw_data_dto import ProductRawDataDto
from schemas.product.modified_product_dto import ModifiedProductDataDto


pytest_plugins = ["tests.fixtures.product.conftest"]


class TestProductIntegration:
    """Product 엔드포인트 통합 테스트"""

    def test_get_products_success(
            self,
            client: TestClient,
            mock_product_read_service
        ):
        """상품 목록 조회 성공 테스트"""
        # Mock ProductReadService
        mock_service = mock_product_read_service
            
        # Mock get_products_by_pagenation 메서드
        
        mock_products = [
            ProductRawDataDto(
                id=1,
                goods_nm="테스트상품1",
                compayny_goods_cd="GOODS001",
                goods_gubun=1,
                class_cd1="001",
                class_cd2="002",
                class_cd3="003",
                class_cd4="004",
                origin="한국",
                goods_season=1,
                sex=1,
                status=1,
                tax_yn=1,
                delv_type=1,
                goods_cost=Decimal("8000"),
                goods_price=Decimal("10000"),
                goods_consumer_price=Decimal("12000"),
                img_path="/images/test1.jpg",
                goods_remarks="테스트 상품 설명1",
                brand_nm="테스트브랜드1",
                maker="테스트제조사1",
                goods_keyword="테스트키워드1",
                created_at=datetime.now(),
                updated_at=None
            ),
            ProductRawDataDto(
                id=2,
                goods_nm="테스트상품2",
                compayny_goods_cd="GOODS002",
                goods_gubun=1,
                class_cd1="001",
                class_cd2="002",
                class_cd3="003",
                class_cd4="004",
                origin="한국",
                goods_season=1,
                sex=1,
                status=1,
                tax_yn=1,
                delv_type=1,
                goods_cost=Decimal("12000"),
                goods_price=Decimal("15000"),
                goods_consumer_price=Decimal("18000"),
                img_path="/images/test2.jpg",
                goods_remarks="테스트 상품 설명2",
                brand_nm="테스트브랜드2",
                maker="테스트제조사2",
                goods_keyword="테스트키워드2",
                created_at=datetime.now(),
                updated_at=None
            )
        ]
        
        mock_service.get_products_by_pagenation.return_value = mock_products
        
        # When: API 요청 실행
        response = client.get("/api/v1/product?page=1")
        
        # Then: 응답 검증
        if response.status_code != 200:
            print(f"Response status: {response.status_code}")
            print(f"Response content: {response.text}")
        assert response.status_code == 200
        response_data = response.json()
        
        # 응답 구조 검증
        assert "products" in response_data
        assert "current_page" in response_data
        assert "page_size" in response_data
        
        # Mock 데이터와 일치하는지 확인
        assert len(response_data["products"]) == 2
        assert response_data["current_page"] == 1
        assert response_data["page_size"] == 20
        
        # 각 상품 데이터 검증
        for i, product in enumerate(response_data["products"]):
            mock_product = mock_products[i]
            assert product["id"] == mock_product.id
            assert product["goods_nm"] == mock_product.goods_nm
            assert float(product["goods_price"]) == float(mock_product.goods_price)
        
        # Mock 메서드가 올바른 파라미터로 호출되었는지 확인
        mock_service.get_products_by_pagenation.assert_called_once_with(page=1)

    def test_bulk_db_to_excel_success(self, client: TestClient, mock_product_read_service):
        """DB to Excel 변환 성공 테스트"""
        # Mock ProductReadService
        mock_service = mock_product_read_service
            
        # Mock convert_product_data_to_excel 메서드
        mock_streaming_response = StreamingResponse(
            iter([b"test excel content"]),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=products.xlsx"}
        )
        
        mock_service.convert_product_data_to_excel.return_value = mock_streaming_response
        
        # When: API 요청 실행
        response = client.get("/api/v1/product/bulk/db-to-excel")
        
        # Then: 응답 검증
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        assert "attachment; filename=products.xlsx" in response.headers["content-disposition"]
        
        # Mock 메서드가 호출되었는지 확인
        mock_service.convert_product_data_to_excel.assert_called_once()

    def test_modify_product_name_success(
            self,
            client: TestClient,
            mock_product_update_service
        ):
        """상품명 수정 성공 테스트"""
        # Mock ProductUpdateService
        mock_service = mock_product_update_service
        
        mock_dto = ModifiedProductDataDto(
            test_product_raw_data_id=1,
            rev=1,
            goods_nm="수정된상품명",
            compayny_goods_cd="GOODS001",
            goods_gubun=1,
            class_cd1="001",
            class_cd2="002",
            class_cd3="003",
            origin="한국",
            goods_season=1,
            sex=1,
            status=1,
            tax_yn=1,
            delv_type=1,
            goods_cost=Decimal("8000"),
            goods_price=Decimal("10000"),
            goods_consumer_price=Decimal("12000"),
            img_path="/images/test.jpg",
            goods_remarks="수정된 상품 설명",
            created_at=None,
            updated_at=None
        )
        
        mock_service.modify_product_name.return_value = mock_dto
        
        # Given: 요청 데이터
        request_data = {
            "compayny_goods_cd": "GOODS001",
            "name": "수정된상품명"
        }
        
        # When: API 요청 실행
        response = client.put("/api/v1/product/name", json=request_data)
        
        # Then: 응답 검증
        assert response.status_code == 200
        response_data = response.json()
        
        # 응답 구조 검증
        assert "company_goods_cd" in response_data
        assert "goods_nm" in response_data
        assert "rev" in response_data
        
        # Mock 데이터와 일치하는지 확인
        assert response_data["company_goods_cd"] == mock_dto.compayny_goods_cd
        assert response_data["goods_nm"] == mock_dto.goods_nm
        assert response_data["rev"] == mock_dto.rev
        
        # Mock 메서드가 올바른 파라미터로 호출되었는지 확인
        mock_service.modify_product_name.assert_called_once_with(
            compayny_goods_cd="GOODS001",
            product_name="수정된상품명"
        )

    def test_db_to_xml_sabangnet_request_all_success(
            self,
            client: TestClient,
            mock_upload_file_to_minio,
            mock_get_minio_file_url,
            mock_product_create_service_request,
            mock_product_registration_xml,
            mock_product_db_xml_usecase
        ):
        """DB to XML 변환 및 사방넷 요청 성공 테스트"""
        # Mock ProductDbXmlUsecase
        mock_usecase = mock_product_db_xml_usecase
            
        # Mock 메서드들 설정
        mock_usecase.db_to_xml_file_all.return_value = "temp_test.xml"
        mock_usecase.get_product_raw_data_count.return_value = 10
        mock_usecase.update_product_id_by_compayny_goods_cd.return_value = None
        
        # Mock 외부 함수들 설정
        mock_upload_file_to_minio.return_value = "test_xml_file.xml"
        mock_get_minio_file_url.return_value = "http://example.com/xml"
        mock_product_create_service_request.return_value = """
        <SABANGNET_PRODUCT_REGISTRATION_RESPONSE>
            <DATA>
                <PRODUCT_ID>12345</PRODUCT_ID>
                <COMPAYNY_GOODS_CD>GOODS001</COMPAYNY_GOODS_CD>
            </DATA>
        </SABANGNET_PRODUCT_REGISTRATION_RESPONSE>
        """
        
        # Mock ProductRegistrationXml 클래스
        mock_xml_instance = mock_product_registration_xml.return_value
        mock_xml_instance.input_product_id_to_db.return_value = [("GOODS001", 12345)]
        
        # When: API 요청 실행
        response = client.post("/api/v1/product/db-to-xml-all/sabangnet-request")
        
        # Then: 응답 검증
        assert response.status_code == 200
        response_data = response.json()
        
        # 응답 구조 검증
        assert "success" in response_data
        assert "message" in response_data
        assert "xml_file_path" in response_data
        assert "processed_count" in response_data
        
        # Mock 데이터와 일치하는지 확인
        assert response_data["success"] is True
        assert "모든 상품 데이터를 XML로 변환하고 사방넷 상품등록 요청했습니다" in response_data["message"]
        assert response_data["xml_file_path"] == "http://example.com/xml"
        assert response_data["processed_count"] == 10
        
        # Mock 메서드들이 호출되었는지 확인
        mock_usecase.db_to_xml_file_all.assert_called_once()
        mock_usecase.get_product_raw_data_count.assert_called_once()
        mock_usecase.update_product_id_by_compayny_goods_cd.assert_called_once_with([("GOODS001", 12345)])

    def test_db_to_xml_sabangnet_request_no_data(self, client: TestClient, mock_product_db_xml_usecase):
        """DB to XML 변환 시 데이터 없음 테스트"""
        # Mock ProductDbXmlUsecase가 ValueError 발생
        mock_usecase = mock_product_db_xml_usecase
            
        # Mock db_to_xml_file_all 메서드가 ValueError 발생
        mock_usecase.db_to_xml_file_all.side_effect = ValueError("데이터가 없습니다")
        
        # When: API 요청 실행
        response = client.post("/api/v1/product/db-to-xml-all/sabangnet-request")
        
        # Then: 404 에러 응답 검증
        assert response.status_code == 404
        response_data = response.json()
        assert response_data["detail"] == "데이터가 없습니다"

    def test_db_to_xml_sabangnet_request_with_test_mode_validation(
            self,
            client: TestClient,
            mock_upload_file_to_minio,
            mock_get_minio_file_url,
            mock_product_create_service_request,
            mock_product_registration_xml,
            mock_product_db_xml_usecase
        ):
        """테스트 모드에서 DB to XML 변환 및 사방넷 요청 테스트"""
        # Mock ProductDbXmlUsecase
        mock_usecase = mock_product_db_xml_usecase
        
        # Mock 메서드들 설정
        mock_usecase.db_to_xml_file_all.return_value = "test_mode_file.xml"
        mock_usecase.get_product_raw_data_count.return_value = 5
        mock_usecase.update_product_id_by_compayny_goods_cd.return_value = None
        
        # Mock 외부 함수들 설정
        mock_upload_file_to_minio.return_value = "test_xml_file.xml"
        mock_get_minio_file_url.return_value = "http://example.com/xml"
        mock_product_create_service_request.return_value = """
        <SABANGNET_PRODUCT_REGISTRATION_RESPONSE>
            <DATA>
                <PRODUCT_ID>67890</PRODUCT_ID>
                <COMPAYNY_GOODS_CD>GOODS002</COMPAYNY_GOODS_CD>
            </DATA>
        </SABANGNET_PRODUCT_REGISTRATION_RESPONSE>
        """
        
        # Mock ProductRegistrationXml 클래스
        mock_xml_instance = mock_product_registration_xml.return_value
        mock_xml_instance.input_product_id_to_db.return_value = [("GOODS002", 67890)]
        
        # When: API 요청 실행
        response = client.post("/api/v1/product/db-to-xml-all/sabangnet-request")
        
        # Then: 응답 검증
        assert response.status_code == 200
        response_data = response.json()
        
        # Mock 데이터와 일치하는지 확인
        assert response_data["success"] is True
        assert response_data["processed_count"] == 5
        assert response_data["xml_file_path"] == "http://example.com/xml"
        
        # Mock 메서드들이 호출되었는지 확인
        mock_usecase.db_to_xml_file_all.assert_called_once()
        mock_usecase.get_product_raw_data_count.assert_called_once()
        mock_usecase.update_product_id_by_compayny_goods_cd.assert_called_once_with([("GOODS002", 67890)])

    def test_modify_product_name_with_mock_db_data_validation(self, client: TestClient, mock_product_update_service):
        """Mock DB 데이터를 사용한 상품명 수정 검증 테스트"""
        # Mock ProductUpdateService
        mock_service = mock_product_update_service
            
        # Mock modify_product_name 메서드
        
        mock_dto = ModifiedProductDataDto(
            test_product_raw_data_id=1,
            rev=1,
            goods_nm="검증된상품명",
            compayny_goods_cd="GOODS001",
            goods_gubun=1,
            class_cd1="001",
            class_cd2="002",
            class_cd3="003",
            origin="한국",
            goods_season=1,
            sex=1,
            status=1,
            tax_yn=1,
            delv_type=1,
            goods_cost=Decimal("9000"),
            goods_price=Decimal("12000"),
            goods_consumer_price=Decimal("14400"),
            img_path="/images/test.jpg",
            goods_remarks="검증된 상품 설명"
        )
        
        mock_service.modify_product_name.return_value = mock_dto
        
        # Given: 요청 데이터
        request_data = {
            "compayny_goods_cd": "GOODS001",
            "name": "검증된상품명"
        }
        
        # When: API 요청 실행
        response = client.put("/api/v1/product/name", json=request_data)
        
        # Then: 응답 검증
        assert response.status_code == 200
        response_data = response.json()
        
        # Mock 데이터와 일치하는지 확인 (ProductNameResponse 구조에 맞게)
        assert response_data["goods_nm"] == mock_dto.goods_nm
        assert response_data["company_goods_cd"] == mock_dto.compayny_goods_cd
        assert response_data["rev"] == mock_dto.rev
        
        # Mock 메서드가 올바른 파라미터로 호출되었는지 확인
        mock_service.modify_product_name.assert_called_once_with(
            compayny_goods_cd="GOODS001",
            product_name="검증된상품명"
        ) 