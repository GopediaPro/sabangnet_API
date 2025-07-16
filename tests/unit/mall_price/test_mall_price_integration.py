import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from tests.mock_db.mock_tables.mall_price import MALL_PRICE
from tests.mock_db.mock_tables.test_product_raw_data import TEST_PRODUCT_RAW_DATA
from services.usecase.product_mall_price_usecase import ProductMallPriceUsecase


class TestMallPriceIntegration:
    """mall_price 엔드포인트 통합 테스트"""
    
    @pytest.fixture
    def mock_usecase(self):
        """ProductMallPriceUsecase 모킹"""
        with patch('api.v1.endpoints.mall_price.ProductMallPriceUsecase') as mock:
            usecase_instance = AsyncMock()
            mock.return_value = usecase_instance
            yield usecase_instance
    
    def test_mall_price_setting_success(self, client: TestClient, mock_usecase: AsyncMock):
        """mall_price 설정 성공 테스트"""
        # Given: 요청 데이터와 예상 응답
        request_data = {
            "compayny_goods_cd": "GOODS001"
        }
        
        expected_response = {
            "message": "상품 가격 설정이 완료되었습니다.",
            "compayny_goods_cd": "GOODS001",
            "product_count": 1
        }
        
        # Mock usecase의 반환값 설정
        mock_usecase.setting_mall_price.return_value = expected_response
        
        # When: API 요청 실행
        response = client.post("/api/v1/mall-price", json=request_data)
        
        # Then: 응답 검증
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["message"] == expected_response["message"]
        assert response_data["compayny_goods_cd"] == expected_response["compayny_goods_cd"]
        assert response_data["product_count"] == expected_response["product_count"]
        
        # Mock이 올바른 파라미터로 호출되었는지 확인
        mock_usecase.setting_mall_price.assert_called_once_with(
            compayny_goods_cd="GOODS001"
        )
    
    def test_mall_price_setting_with_mock_db_data(self, client: TestClient, mock_usecase: AsyncMock):
        """mock DB 데이터를 사용한 mall_price 설정 테스트"""
        # Given: mock DB의 실제 데이터 사용
        mock_product = MALL_PRICE[0]  # 첫 번째 상품 데이터
        
        request_data = {
            "compayny_goods_cd": mock_product["compayny_goods_cd"]
        }
        
        # Mock usecase가 실제 mock DB 데이터를 기반으로 응답하도록 설정
        expected_response = {
            "message": "상품 가격 설정이 완료되었습니다.",
            "compayny_goods_cd": mock_product["compayny_goods_cd"],
            "product_count": 1,
            "product_name": mock_product["product_nm"],
            "standard_price": mock_product["standard_price"]
        }
        
        mock_usecase.setting_mall_price.return_value = expected_response
        
        # When: API 요청 실행
        response = client.post("/api/v1/mall-price", json=request_data)
        
        # Then: 응답 검증
        assert response.status_code == 200
        response_data = response.json()
        
        # Mock DB 데이터와 일치하는지 확인
        assert response_data["compayny_goods_cd"] == mock_product["compayny_goods_cd"]
        assert response_data["product_name"] == mock_product["product_nm"]
        assert response_data["standard_price"] == mock_product["standard_price"]
    
    def test_mall_price_setting_invalid_goods_code(self, client: TestClient, mock_usecase: AsyncMock):
        """존재하지 않는 상품코드로 mall_price 설정 실패 테스트"""
        # Given: 존재하지 않는 상품코드
        request_data = {
            "compayny_goods_cd": "INVALID_GOODS_CODE"
        }
        
        # Mock usecase가 예외를 발생시키도록 설정
        mock_usecase.setting_mall_price.side_effect = Exception("상품을 찾을 수 없습니다.")
        
        # When: API 요청 실행
        response = client.post("/api/v1/mall-price", json=request_data)
        
        # Then: 에러 응답 검증
        assert response.status_code == 500
        response_data = response.json()
        assert "상품을 찾을 수 없습니다." in response_data["detail"]
    
    def test_mall_price_setting_price_range_error(self, client: TestClient, mock_usecase: AsyncMock):
        """가격 범위 초과 에러 테스트"""
        # Given: 요청 데이터
        request_data = {
            "compayny_goods_cd": "GOODS001"
        }
        
        # Mock usecase가 DBAPIError를 발생시키도록 설정
        from sqlalchemy.exc import DBAPIError
        mock_usecase.setting_mall_price.side_effect = DBAPIError(
            "value out of int32 range", None, None
        )
        
        # When: API 요청 실행
        response = client.post("/api/v1/mall-price", json=request_data)
        
        # Then: 에러 응답 검증
        assert response.status_code == 400
        response_data = response.json()
        assert "원본 상품 가격이 너무 커서 계산할 수 없습니다." in response_data["detail"]
    
    def test_mall_price_setting_missing_required_field(self, client: TestClient):
        """필수 필드 누락 테스트"""
        # Given: 필수 필드가 누락된 요청
        request_data = {}
        
        # When: API 요청 실행
        response = client.post("/api/v1/mall-price", json=request_data)
        
        # Then: 검증 에러 응답
        assert response.status_code == 422
        response_data = response.json()
        assert "compayny_goods_cd" in str(response_data)
    
    def test_mall_price_setting_empty_goods_code(self, client: TestClient):
        """빈 상품코드 테스트"""
        # Given: 빈 상품코드
        request_data = {
            "compayny_goods_cd": ""
        }
        
        # When: API 요청 실행
        response = client.post("/api/v1/mall-price", json=request_data)
        
        # Then: 검증 에러 응답
        assert response.status_code == 422
    
    def test_mall_price_setting_with_multiple_mock_products(self, client: TestClient, mock_usecase: AsyncMock):
        """여러 mock 상품 데이터를 사용한 테스트"""
        # Given: 여러 mock 상품 데이터 사용
        test_products = [
            MALL_PRICE[0],  # 첫 번째 상품
            MALL_PRICE[1]   # 두 번째 상품
        ]
        
        for i, product in enumerate(test_products):
            request_data = {
                "compayny_goods_cd": product["compayny_goods_cd"]
            }
            
            expected_response = {
                "message": "상품 가격 설정이 완료되었습니다.",
                "compayny_goods_cd": product["compayny_goods_cd"],
                "product_count": 1,
                "product_name": product["product_nm"],
                "standard_price": product["standard_price"]
            }
            
            mock_usecase.setting_mall_price.return_value = expected_response
            
            # When: API 요청 실행
            response = client.post("/api/v1/mall-price", json=request_data)
            
            # Then: 응답 검증
            assert response.status_code == 200
            response_data = response.json()
            
            # Mock DB 데이터와 일치하는지 확인
            assert response_data["compayny_goods_cd"] == product["compayny_goods_cd"]
            assert response_data["product_name"] == product["product_nm"]
            assert response_data["standard_price"] == product["standard_price"]
            
            # Mock 호출 확인
            mock_usecase.setting_mall_price.assert_called_with(
                compayny_goods_cd=product["compayny_goods_cd"]
            ) 