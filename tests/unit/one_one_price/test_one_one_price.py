"""
1+1 가격 API 테스트
"""
import pytest

from fastapi import FastAPI
from fastapi.testclient import TestClient

from unittest.mock import AsyncMock, MagicMock
from utils.logs.sabangnet_logger import get_logger

from api.v1.endpoints.one_one_price import get_product_one_one_price_usecase

logger = get_logger(__name__)


@pytest.mark.api
class TestOneOnePriceAPI:
    """1+1 가격 API 테스트 클래스"""

    def test_one_one_price_setting_success(self, test_app: FastAPI, async_client: TestClient):
        """1+1 가격 설정 성공 테스트"""
        try:
            logger.info("1+1 가격 설정 성공 테스트 시작")
            
            test_data = {
                "product_nm": "테스트상품1",
                "gubun": "마스터"
            }
            
            mock_dto = {
                "id": 1,
                "test_product_raw_data_id": 1,
                "product_nm": "테스트상품1",
                "compayny_goods_cd": "GOODS001",
                "standard_price": 10000,
                "one_one_price": 22000,
                "shop0007": 25200,
                "shop0042": 25200
            }
            
            mock_usecase = MagicMock()
            mock_usecase.calculate_and_save_one_one_price = AsyncMock(return_value=mock_dto)
            
            test_app.dependency_overrides[get_product_one_one_price_usecase] = lambda: mock_usecase
            
            try:
                response = async_client.post("/api/v1/one-one-price/", json=test_data)
                
                assert response.status_code == 200
                data = response.json()
                assert "id" in data
                assert data["product_nm"] == "테스트상품1"
                
            finally:
                test_app.dependency_overrides = {}
                
            logger.info("1+1 가격 설정 성공 테스트 완료")
        except Exception as e:
            logger.error(f"1+1 가격 설정 성공 테스트 실패: {e}")
            raise e

    def test_one_one_price_setting_invalid_request(self, async_client: TestClient):
        """1+1 가격 설정 잘못된 요청 테스트"""
        try:
            logger.info("1+1 가격 설정 잘못된 요청 테스트 시작")
            
            # 필수 필드가 없는 요청
            test_data = {}
            
            response = async_client.post("/api/v1/one-one-price/", json=test_data)
            
            assert response.status_code == 422  # Validation Error
            
            logger.info("1+1 가격 설정 잘못된 요청 테스트 완료")
        except Exception as e:
            logger.error(f"1+1 가격 설정 잘못된 요청 테스트 실패: {e}")
            raise e

    def test_one_one_price_setting_db_error(self, test_app: FastAPI, async_client: TestClient):
        """1+1 가격 설정 DB 에러 테스트"""
        try:
            logger.info("1+1 가격 설정 DB 에러 테스트 시작")
            
            test_data = {
                "product_nm": "테스트상품1",
                "gubun": "마스터"
            }
            
            mock_usecase = MagicMock()
            mock_usecase.calculate_and_save_one_one_price = AsyncMock(side_effect=Exception("integer out of range"))
            
            test_app.dependency_overrides[get_product_one_one_price_usecase] = lambda: mock_usecase
            
            try:
                response = async_client.post("/api/v1/one-one-price/", json=test_data)
                
                assert response.status_code == 500
                data = response.json()
                assert "detail" in data
                
            finally:
                test_app.dependency_overrides = {}
                
            logger.info("1+1 가격 설정 DB 에러 테스트 완료")
        except Exception as e:
            logger.error(f"1+1 가격 설정 DB 에러 테스트 실패: {e}")
            raise e

    def test_one_one_price_bulk_setting_success(self, test_app: FastAPI, async_client: TestClient):
        """1+1 가격 벌크 설정 성공 테스트"""
        try:
            logger.info("1+1 가격 벌크 설정 성공 테스트 시작")
            
            test_data = {
                "items": [
                    {
                        "product_nm": "테스트상품1",
                        "gubun": "마스터"
                    },
                    {
                        "product_nm": "테스트상품2",
                        "gubun": "전문몰"
                    }
                ]
            }
            
            mock_dto_list = [
                {
                    "id": 1,
                    "test_product_raw_data_id": 1,
                    "product_nm": "테스트상품1",
                    "compayny_goods_cd": "GOODS001",
                    "standard_price": 10000,
                    "one_one_price": 22000
                },
                {
                    "id": 2,
                    "test_product_raw_data_id": 2,
                    "product_nm": "테스트상품2",
                    "compayny_goods_cd": "GOODS002",
                    "standard_price": 20000,
                    "one_one_price": 42000
                }
            ]
            
            mock_usecase = MagicMock()
            mock_usecase.calculate_and_save_one_one_prices_bulk = AsyncMock(return_value=mock_dto_list)
            
            test_app.dependency_overrides[get_product_one_one_price_usecase] = lambda: mock_usecase
            
            try:
                response = async_client.post("/api/v1/one-one-price/bulk", json=test_data)
                
                assert response.status_code == 200
                data = response.json()
                assert "items" in data
                assert len(data["items"]) == 2
                
            finally:
                test_app.dependency_overrides = {}
                
            logger.info("1+1 가격 벌크 설정 성공 테스트 완료")
        except Exception as e:
            logger.error(f"1+1 가격 벌크 설정 성공 테스트 실패: {e}")
            raise e

    def test_one_one_price_bulk_setting_invalid_request(self, async_client: TestClient):
        """1+1 가격 벌크 설정 잘못된 요청 테스트"""
        try:
            logger.info("1+1 가격 벌크 설정 잘못된 요청 테스트 시작")
            
            # 필수 필드가 없는 요청
            test_data = {}
            
            response = async_client.post("/api/v1/one-one-price/bulk", json=test_data)
            
            assert response.status_code == 422  # Validation Error
            
            logger.info("1+1 가격 벌크 설정 잘못된 요청 테스트 완료")
        except Exception as e:
            logger.error(f"1+1 가격 벌크 설정 잘못된 요청 테스트 실패: {e}")
            raise e

    def test_one_one_price_bulk_setting_db_error(self, test_app: FastAPI, async_client: TestClient):
        """1+1 가격 벌크 설정 DB 에러 테스트"""
        try:
            logger.info("1+1 가격 벌크 설정 DB 에러 테스트 시작")
            
            test_data = {
                "items": [
                    {
                        "product_nm": "테스트상품1",
                        "gubun": "마스터"
                    }
                ]
            }
            
            mock_usecase = MagicMock()
            mock_usecase.calculate_and_save_one_one_prices_bulk = AsyncMock(side_effect=Exception("integer out of range"))
            
            test_app.dependency_overrides[get_product_one_one_price_usecase] = lambda: mock_usecase
            
            try:
                response = async_client.post("/api/v1/one-one-price/bulk", json=test_data)
                
                assert response.status_code == 500
                data = response.json()
                assert "detail" in data
                
            finally:
                test_app.dependency_overrides = {}
                
            logger.info("1+1 가격 벌크 설정 DB 에러 테스트 완료")
        except Exception as e:
            logger.error(f"1+1 가격 벌크 설정 DB 에러 테스트 실패: {e}")
            raise e

    def test_one_one_price_setting_empty_product(self, test_app: FastAPI, async_client: TestClient):
        """1+1 가격 설정 빈 상품명 테스트"""
        try:
            logger.info("1+1 가격 설정 빈 상품명 테스트 시작")
            
            test_data = {
                "product_nm": "",
                "gubun": "마스터"
            }
            
            mock_usecase = MagicMock()
            mock_usecase.calculate_and_save_one_one_price = AsyncMock(side_effect=Exception("상품을 찾을 수 없습니다"))
            
            test_app.dependency_overrides[get_product_one_one_price_usecase] = lambda: mock_usecase
            
            try:
                response = async_client.post("/api/v1/one-one-price/", json=test_data)
                
                assert response.status_code == 500
                data = response.json()
                assert "detail" in data
                
            finally:
                test_app.dependency_overrides = {}
                
            logger.info("1+1 가격 설정 빈 상품명 테스트 완료")
        except Exception as e:
            logger.error(f"1+1 가격 설정 빈 상품명 테스트 실패: {e}")
            raise e
