import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from tests.mock_db.mock_tables.one_one_price import ONE_ONE_PRICE
from tests.mock_db.mock_tables.test_product_raw_data import TEST_PRODUCT_RAW_DATA
from services.usecase.product_one_one_price_usecase import ProductOneOnePriceUsecase


class TestOneOnePriceIntegration:
    """one_one_price 엔드포인트 통합 테스트"""
    
    @pytest.fixture
    def mock_usecase(self):
        """ProductOneOnePriceUsecase 모킹"""
        with patch('api.v1.endpoints.one_one_price.ProductOneOnePriceUsecase') as mock:
            usecase_instance = AsyncMock()
            mock.return_value = usecase_instance
            yield usecase_instance
    
    def test_one_one_price_setting_success(self, client: TestClient, mock_usecase: AsyncMock):
        """1+1 가격 설정 성공 테스트"""
        # Given: 요청 데이터와 예상 응답
        request_data = {
            "product_nm": "테스트상품1",
            "gubun": "1+1"
        }
        
        expected_response = {
            "message": "1+1 가격 계산이 완료되었습니다.",
            "product_nm": "테스트상품1",
            "gubun": "1+1",
            "one_one_price": 22000
        }
        
        # Mock usecase의 반환값 설정
        mock_usecase.calculate_and_save_one_one_price.return_value = expected_response
        
        # When: API 요청 실행
        response = client.post("/api/v1/one-one-price/", json=request_data)
        
        # Then: 응답 검증
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["message"] == expected_response["message"]
        assert response_data["product_nm"] == expected_response["product_nm"]
        assert response_data["gubun"] == expected_response["gubun"]
        assert response_data["one_one_price"] == expected_response["one_one_price"]
        
        # Mock이 올바른 파라미터로 호출되었는지 확인
        mock_usecase.calculate_and_save_one_one_price.assert_called_once_with(
            product_nm="테스트상품1",
            gubun="1+1"
        )
    
    def test_one_one_price_setting_with_mock_db_data(self, client: TestClient, mock_usecase: AsyncMock):
        """mock DB 데이터를 사용한 1+1 가격 설정 테스트"""
        # Given: mock DB의 실제 데이터 사용
        mock_product = ONE_ONE_PRICE[0]  # 첫 번째 상품 데이터
        
        request_data = {
            "product_nm": mock_product["product_nm"],
            "gubun": "1+1"
        }
        
        # Mock usecase가 실제 mock DB 데이터를 기반으로 응답하도록 설정
        expected_response = {
            "message": "1+1 가격 계산이 완료되었습니다.",
            "product_nm": mock_product["product_nm"],
            "gubun": "1+1",
            "one_one_price": float(mock_product["one_one_price"]),
            "standard_price": mock_product["standard_price"],
            "compayny_goods_cd": mock_product["compayny_goods_cd"]
        }
        
        mock_usecase.calculate_and_save_one_one_price.return_value = expected_response
        
        # When: API 요청 실행
        response = client.post("/api/v1/one-one-price/", json=request_data)
        
        # Then: 응답 검증
        assert response.status_code == 200
        response_data = response.json()
        
        # Mock DB 데이터와 일치하는지 확인
        assert response_data["product_nm"] == mock_product["product_nm"]
        assert response_data["one_one_price"] == float(mock_product["one_one_price"])
        assert response_data["standard_price"] == mock_product["standard_price"]
        assert response_data["compayny_goods_cd"] == mock_product["compayny_goods_cd"]
    
    def test_one_one_price_bulk_setting_success(self, client: TestClient, mock_usecase: AsyncMock):
        """1+1 가격 대량 설정 성공 테스트"""
        # Given: 대량 요청 데이터
        request_data = {
            "product1": {
                "product_nm": "테스트상품1",
                "gubun": "1+1"
            },
            "product2": {
                "product_nm": "테스트상품2", 
                "gubun": "1+1"
            }
        }
        
        expected_response = {
            "message": "1+1 가격 대량 계산이 완료되었습니다.",
            "processed_count": 2,
            "results": [
                {
                    "product_nm": "테스트상품1",
                    "one_one_price": 22000
                },
                {
                    "product_nm": "테스트상품2",
                    "one_one_price": 42000
                }
            ]
        }
        
        # Mock usecase의 반환값 설정
        mock_usecase.calculate_and_save_one_one_prices_bulk.return_value = expected_response
        
        # When: API 요청 실행
        response = client.post("/api/v1/one-one-price/bulk", json=request_data)
        
        # Then: 응답 검증
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["message"] == expected_response["message"]
        assert response_data["processed_count"] == expected_response["processed_count"]
        assert len(response_data["results"]) == 2
    
    def test_one_one_price_bulk_setting_with_mock_db_data(self, client: TestClient, mock_usecase: AsyncMock):
        """mock DB 데이터를 사용한 1+1 가격 대량 설정 테스트"""
        # Given: mock DB의 실제 데이터 사용
        mock_products = ONE_ONE_PRICE[:2]  # 첫 두 개 상품 데이터
        
        request_data = {
            f"product{i+1}": {
                "product_nm": product["product_nm"],
                "gubun": "1+1"
            }
            for i, product in enumerate(mock_products)
        }
        
        # Mock usecase가 실제 mock DB 데이터를 기반으로 응답하도록 설정
        expected_response = {
            "message": "1+1 가격 대량 계산이 완료되었습니다.",
            "processed_count": len(mock_products),
            "results": [
                {
                    "product_nm": product["product_nm"],
                    "one_one_price": float(product["one_one_price"]),
                    "standard_price": product["standard_price"],
                    "compayny_goods_cd": product["compayny_goods_cd"]
                }
                for product in mock_products
            ]
        }
        
        mock_usecase.calculate_and_save_one_one_prices_bulk.return_value = expected_response
        
        # When: API 요청 실행
        response = client.post("/api/v1/one-one-price/bulk", json=request_data)
        
        # Then: 응답 검증
        assert response.status_code == 200
        response_data = response.json()
        
        # Mock DB 데이터와 일치하는지 확인
        assert response_data["processed_count"] == len(mock_products)
        for i, result in enumerate(response_data["results"]):
            mock_product = mock_products[i]
            assert result["product_nm"] == mock_product["product_nm"]
            assert result["one_one_price"] == float(mock_product["one_one_price"])
            assert result["standard_price"] == mock_product["standard_price"]
            assert result["compayny_goods_cd"] == mock_product["compayny_goods_cd"]
    
    def test_one_one_price_setting_invalid_product(self, client: TestClient, mock_usecase: AsyncMock):
        """존재하지 않는 상품으로 1+1 가격 설정 실패 테스트"""
        # Given: 존재하지 않는 상품명
        request_data = {
            "product_nm": "존재하지않는상품",
            "gubun": "1+1"
        }
        
        # Mock usecase가 예외를 발생시키도록 설정
        mock_usecase.calculate_and_save_one_one_price.side_effect = Exception("상품을 찾을 수 없습니다.")
        
        # When: API 요청 실행
        response = client.post("/api/v1/one-one-price/", json=request_data)
        
        # Then: 에러 응답 검증
        assert response.status_code == 500
        response_data = response.json()
        assert "상품을 찾을 수 없습니다." in response_data["detail"]
    
    def test_one_one_price_setting_price_range_error(self, client: TestClient, mock_usecase: AsyncMock):
        """가격 범위 초과 에러 테스트"""
        # Given: 요청 데이터
        request_data = {
            "product_nm": "테스트상품1",
            "gubun": "1+1"
        }
        
        # Mock usecase가 DBAPIError를 발생시키도록 설정
        from sqlalchemy.exc import DBAPIError
        mock_usecase.calculate_and_save_one_one_price.side_effect = DBAPIError(
            "integer out of range", None, None
        )
        
        # When: API 요청 실행
        response = client.post("/api/v1/one-one-price/", json=request_data)
        
        # Then: 에러 응답 검증
        assert response.status_code == 400
        response_data = response.json()
        assert "원본 상품 가격이 너무 커서 계산할 수 없습니다." in response_data["detail"]
    
    def test_one_one_price_setting_missing_required_fields(self, client: TestClient):
        """필수 필드 누락 테스트"""
        # Given: 필수 필드가 누락된 요청
        request_data = {
            "product_nm": "테스트상품1"
            # gubun 필드 누락
        }
        
        # When: API 요청 실행
        response = client.post("/api/v1/one-one-price/", json=request_data)
        
        # Then: 검증 에러 응답
        assert response.status_code == 422
        response_data = response.json()
        assert "gubun" in str(response_data)
    
    def test_one_one_price_setting_empty_fields(self, client: TestClient):
        """빈 필드 테스트"""
        # Given: 빈 필드들
        request_data = {
            "product_nm": "",
            "gubun": ""
        }
        
        # When: API 요청 실행
        response = client.post("/api/v1/one-one-price/", json=request_data)
        
        # Then: 검증 에러 응답
        assert response.status_code == 422
    
    def test_one_one_price_setting_with_multiple_mock_products(self, client: TestClient, mock_usecase: AsyncMock):
        """여러 mock 상품 데이터를 사용한 테스트"""
        # Given: 여러 mock 상품 데이터 사용
        test_products = [
            ONE_ONE_PRICE[0],  # 첫 번째 상품
            ONE_ONE_PRICE[1]   # 두 번째 상품
        ]
        
        for i, product in enumerate(test_products):
            request_data = {
                "product_nm": product["product_nm"],
                "gubun": "1+1"
            }
            
            expected_response = {
                "message": "1+1 가격 계산이 완료되었습니다.",
                "product_nm": product["product_nm"],
                "gubun": "1+1",
                "one_one_price": float(product["one_one_price"]),
                "standard_price": product["standard_price"],
                "compayny_goods_cd": product["compayny_goods_cd"]
            }
            
            mock_usecase.calculate_and_save_one_one_price.return_value = expected_response
            
            # When: API 요청 실행
            response = client.post("/api/v1/one-one-price/", json=request_data)
            
            # Then: 응답 검증
            assert response.status_code == 200
            response_data = response.json()
            
            # Mock DB 데이터와 일치하는지 확인
            assert response_data["product_nm"] == product["product_nm"]
            assert response_data["one_one_price"] == float(product["one_one_price"])
            assert response_data["standard_price"] == product["standard_price"]
            assert response_data["compayny_goods_cd"] == product["compayny_goods_cd"]
            
            # Mock 호출 확인
            mock_usecase.calculate_and_save_one_one_price.assert_called_with(
                product_nm=product["product_nm"],
                gubun="1+1"
            ) 