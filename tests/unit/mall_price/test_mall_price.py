"""
쇼핑몰 가격 API 테스트
"""
import pytest

from fastapi import FastAPI
from fastapi.testclient import TestClient

from unittest.mock import AsyncMock, MagicMock

from utils.logs.sabangnet_logger import get_logger

from api.v1.endpoints.mall_price import get_product_mall_price_usecase


logger = get_logger(__name__)


@pytest.mark.api
class TestMallPriceAPI:
    """쇼핑몰 가격 API 테스트 클래스"""

    def test_mall_price_setting_success(self, test_app: FastAPI, async_client: TestClient):
        """쇼핑몰 가격 설정 성공 테스트"""
        try:
            logger.info("쇼핑몰 가격 설정 성공 테스트 시작")
            
            test_data = {
                "compayny_goods_cd": "GOODS001"
            }
            
            mock_result = {
                "success": True,
                "message": "가격 설정 완료",
                "data": {
                    "compayny_goods_cd": "GOODS001",
                    "standard_price": 10000,
                    "shop0007": 12400,
                    "shop0042": 12400
                }
            }
            
            mock_usecase = MagicMock()
            mock_usecase.setting_mall_price = AsyncMock(return_value=mock_result)
            
            test_app.dependency_overrides[get_product_mall_price_usecase] = lambda: mock_usecase
            
            try:
                response = async_client.post("/api/v1/mall-price", data=test_data)
                
                assert response.status_code == 200
                data = response.json()
                assert "success" in data
                assert data["success"] is True
                
            finally:
                test_app.dependency_overrides = {}
                
            logger.info("쇼핑몰 가격 설정 성공 테스트 완료")
        except Exception as e:
            logger.error(f"쇼핑몰 가격 설정 성공 테스트 실패: {e}")
            raise e

    def test_mall_price_setting_db_error(self, test_app: FastAPI, async_client: TestClient):
        """쇼핑몰 가격 설정 DB 에러 테스트"""
        try:
            logger.info("쇼핑몰 가격 설정 DB 에러 테스트 시작")
            
            test_data = {
                "compayny_goods_cd": "GOODS001"
            }
            
            mock_usecase = MagicMock()
            mock_usecase.setting_mall_price = AsyncMock(side_effect=Exception("value out of int32 range"))
            
            test_app.dependency_overrides[get_product_mall_price_usecase] = lambda: mock_usecase
            
            try:
                response = async_client.post("/api/v1/mall-price", data=test_data)
                
                assert response.status_code == 500
                data = response.json()
                assert "detail" in data
                
            finally:
                test_app.dependency_overrides = {}
                
            logger.info("쇼핑몰 가격 설정 DB 에러 테스트 완료")
        except Exception as e:
            logger.error(f"쇼핑몰 가격 설정 DB 에러 테스트 실패: {e}")
            raise e

    def test_mall_price_setting_invalid_request(self, async_client: TestClient):
        """쇼핑몰 가격 설정 잘못된 요청 테스트"""
        try:
            logger.info("쇼핑몰 가격 설정 잘못된 요청 테스트 시작")
            
            # 필수 필드가 없는 요청
            test_data = {}
            
            response = async_client.post("/api/v1/mall-price", json=test_data)
            
            assert response.status_code == 422  # Validation Error
            
            logger.info("쇼핑몰 가격 설정 잘못된 요청 테스트 완료")
        except Exception as e:
            logger.error(f"쇼핑몰 가격 설정 잘못된 요청 테스트 실패: {e}")
            raise e

    def test_mall_price_setting_empty_goods_cd(self, test_app: FastAPI, async_client: TestClient):
        """쇼핑몰 가격 설정 빈 상품코드 테스트"""
        try:
            logger.info("쇼핑몰 가격 설정 빈 상품코드 테스트 시작")
            
            test_data = {
                "compayny_goods_cd": ""
            }
            
            mock_usecase = MagicMock()
            mock_usecase.setting_mall_price = AsyncMock(side_effect=Exception("상품코드를 찾을 수 없습니다"))
            
            test_app.dependency_overrides[get_product_mall_price_usecase] = lambda: mock_usecase
            
            try:
                response = async_client.post("/api/v1/mall-price", data=test_data)
                
                assert response.status_code == 500
                data = response.json()
                assert "detail" in data
                
            finally:
                test_app.dependency_overrides = {}
                
            logger.info("쇼핑몰 가격 설정 빈 상품코드 테스트 완료")
        except Exception as e:
            logger.error(f"쇼핑몰 가격 설정 빈 상품코드 테스트 실패: {e}")
            raise e

    def test_mall_price_setting_large_price_error(self, test_app: FastAPI, async_client: TestClient):
        """쇼핑몰 가격 설정 큰 가격 에러 테스트"""
        try:
            logger.info("쇼핑몰 가격 설정 큰 가격 에러 테스트 시작")
            
            test_data = {
                "compayny_goods_cd": "GOODS001"
            }
            
            mock_usecase = MagicMock()
            mock_usecase.setting_mall_price = AsyncMock(side_effect=Exception("value out of int32 range"))
            
            test_app.dependency_overrides[get_product_mall_price_usecase] = lambda: mock_usecase
            
            try:
                response = async_client.post("/api/v1/mall-price", data=test_data)
                
                assert response.status_code == 500
                data = response.json()
                assert "detail" in data
                
            finally:
                test_app.dependency_overrides = {}
                
            logger.info("쇼핑몰 가격 설정 큰 가격 에러 테스트 완료")
        except Exception as e:
            logger.error(f"쇼핑몰 가격 설정 큰 가격 에러 테스트 실패: {e}")
            raise e
