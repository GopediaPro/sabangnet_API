from decimal import Decimal
from tests.mocks import MOCK_TABLES
from sqlalchemy.exc import DBAPIError
from fastapi.testclient import TestClient
from utils.logs.sabangnet_logger import get_logger
from services.one_one_price.one_one_price_service import OneOnePriceCalculator
from schemas.one_one_price.one_one_price_dto import OneOnePriceDto, OneOnePriceBulkDto


logger = get_logger(__name__)


pytest_plugins = ["tests.fixtures.one_one_price.conftest"]


class TestOneOnePriceIntegration:
    """
    One One Price 엔드포인트 통합 테스트
    두 번째 mock 상품 데이터로 진행
    """

    def test_one_one_price_setting_success(
            self,
            client: TestClient,
            mock_product_one_one_price_usecase,
            sample_one_one_price_request_data,
            expected_one_one_price_dto_from_second_data
        ):
        """1+1 가격 설정 성공 테스트"""

        # Mock ProductOneOnePriceUsecase
        mock_calculate = mock_product_one_one_price_usecase.calculate_and_save_one_one_price
        target_product = None

        found = False
        for mock_data in MOCK_TABLES["product_raw_data"]:
            if (
                mock_data["product_nm"] == sample_one_one_price_request_data["product_nm"] and
                mock_data["gubun"] == sample_one_one_price_request_data["gubun"]):
                target_product = mock_data
                found = True
                break
        else:
            if not found:
                raise ValueError("상품 데이터를 찾을 수 없습니다.")

        # 2번째 mock 상품 데이터로 진행했을때 예상 결과값
        mock_calculate.return_value = expected_one_one_price_dto_from_second_data
        
        # When: API 요청 실행
        response = client.post("/api/v1/one-one-price/", json=sample_one_one_price_request_data)
        
        # Then: 응답 검증
        assert response.status_code == 200
        response_data = response.json()
        
        # 응답 구조 검증 (실제 API 응답 구조에 맞게)
        assert "group_115" in response_data
        assert "group_105" in response_data
        assert "group_same" in response_data
        assert "group_plus100" in response_data
        assert "created_at" in response_data
        
        # Mock 데이터와 일치하는지 확인
        expected_data = expected_one_one_price_dto_from_second_data
        assert response_data["group_115"] == float(expected_data.shop0007)
        assert response_data["group_105"] == float(expected_data.shop0029)
        assert response_data["group_same"] == float(expected_data.shop0381)
        assert response_data["group_plus100"] == float(expected_data.shop0055)
        
        # Mock 메서드가 올바른 파라미터로 호출되었는지 확인
        mock_calculate.assert_called_once_with(
            product_nm="테스트상품2",
            gubun="1+1"
        )

    def test_one_one_price_bulk_setting_success(
            self,
            client: TestClient,
            mock_product_one_one_price_usecase,
            sample_one_one_price_bulk_request_data
        ):
        """1+1 가격 대량 설정 성공 테스트"""
        
        # Mock ProductOneOnePriceUsecase
        mock_calculate_bulk = mock_product_one_one_price_usecase.calculate_and_save_one_one_prices_bulk
        
        # Mock DTO 생성
        mock_dto1 = OneOnePriceDto(
            test_product_raw_data_id=2,
            product_nm="테스트상품2",
            compayny_goods_cd="GOODS002",
            standard_price=Decimal("14000"),  # i=2: 12000 + 2*1000 = 14000
            one_one_price=Decimal("28900"),
            shop0007=Decimal("33900"),  # group_115
            shop0042=Decimal("33900"),  # group_115
            shop0087=Decimal("33900"),  # group_115
            shop0094=Decimal("33900"),  # group_115
            shop0121=Decimal("33900"),  # group_115
            shop0129=Decimal("33900"),  # group_115
            shop0154=Decimal("33900"),  # group_115
            shop0650=Decimal("33900"),  # group_115
            shop0029=Decimal("30900"),  # group_105
            shop0189=Decimal("30900"),  # group_105
            shop0322=Decimal("30900"),  # group_105
            shop0444=Decimal("30900"),  # group_105
            shop0100=Decimal("30900"),  # group_105
            shop0298=Decimal("30900"),  # group_105
            shop0372=Decimal("30900"),  # group_105
            shop0381=Decimal("28900"),  # group_same
            shop0416=Decimal("28900"),  # group_same
            shop0449=Decimal("28900"),  # group_same
            shop0498=Decimal("28900"),  # group_same
            shop0583=Decimal("28900"),  # group_same
            shop0587=Decimal("28900"),  # group_same
            shop0661=Decimal("28900"),  # group_same
            shop0075=Decimal("28900"),  # group_same
            shop0319=Decimal("28900"),  # group_same
            shop0365=Decimal("28900"),  # group_same
            shop0387=Decimal("28900"),  # group_same
            shop0055=Decimal("29000"),  # group_plus100
            shop0067=Decimal("29000"),  # group_plus100
            shop0068=Decimal("29000"),  # group_plus100
            shop0273=Decimal("29000"),  # group_plus100
            shop0464=Decimal("29000")   # group_plus100
        )
        
        mock_dto2 = OneOnePriceDto(
            test_product_raw_data_id=5,
            product_nm="테스트상품5",
            compayny_goods_cd="GOODS005",
            standard_price=Decimal("17000"),
            one_one_price=Decimal("34900"),
            shop0007=Decimal("40900"),  # group_115
            shop0042=Decimal("40900"),  # group_115
            shop0087=Decimal("40900"),  # group_115
            shop0094=Decimal("40900"),  # group_115
            shop0121=Decimal("40900"),  # group_115
            shop0129=Decimal("40900"),  # group_115
            shop0154=Decimal("40900"),  # group_115
            shop0650=Decimal("40900"),  # group_115
            shop0029=Decimal("37900"),  # group_105
            shop0189=Decimal("37900"),  # group_105
            shop0322=Decimal("37900"),  # group_105
            shop0444=Decimal("37900"),  # group_105
            shop0100=Decimal("37900"),  # group_105
            shop0298=Decimal("37900"),  # group_105
            shop0372=Decimal("37900"),  # group_105
            shop0381=Decimal("34900"),  # group_same
            shop0416=Decimal("34900"),  # group_same
            shop0449=Decimal("34900"),  # group_same
            shop0498=Decimal("34900"),  # group_same
            shop0583=Decimal("34900"),  # group_same
            shop0587=Decimal("34900"),  # group_same
            shop0661=Decimal("34900"),  # group_same
            shop0075=Decimal("34900"),  # group_same
            shop0319=Decimal("34900"),  # group_same
            shop0365=Decimal("34900"),  # group_same
            shop0387=Decimal("34900"),  # group_same
            shop0055=Decimal("35000"),  # group_plus100
            shop0067=Decimal("35000"),  # group_plus100
            shop0068=Decimal("35000"),  # group_plus100
            shop0273=Decimal("35000"),  # group_plus100
            shop0464=Decimal("35000")   # group_plus100
        )
        
        mock_bulk_dto = OneOnePriceBulkDto(
            success_count=2,
            error_count=0,
            created_product_nm=["테스트상품2", "테스트상품5"],
            errors=[],
            success_data=[mock_dto1, mock_dto2]
        )
        
        mock_calculate_bulk.return_value = mock_bulk_dto
        
        # When: API 요청 실행
        response = client.post("/api/v1/one-one-price/bulk", json=sample_one_one_price_bulk_request_data)
        
        # Then: 응답 검증
        assert response.status_code == 200
        response_data = response.json()
        
        # 응답 구조 검증
        assert "success_count" in response_data
        assert "error_count" in response_data
        assert "created_product_nm" in response_data
        assert "errors" in response_data
        assert "success_data" in response_data
        
        # Mock 데이터와 일치하는지 확인
        assert response_data["success_count"] == 2
        assert response_data["error_count"] == 0
        assert response_data["created_product_nm"] == ["테스트상품2", "테스트상품5"]
        assert response_data["errors"] == []
        assert len(response_data["success_data"]) == 2
        
        # Mock 메서드가 올바른 파라미터로 호출되었는지 확인
        # API에서 JSON을 받아서 Pydantic 모델로 변환하므로 OneOnePriceCreate 객체 리스트가 전달됨
        call_args = mock_calculate_bulk.call_args
        assert call_args is not None
        assert "product_nm_and_gubun_list" in call_args.kwargs
        product_list = call_args.kwargs["product_nm_and_gubun_list"]
        assert len(product_list) == 2
        assert product_list[0].product_nm == "테스트상품2"
        assert product_list[0].gubun == "1+1"
        assert product_list[1].product_nm == "테스트상품5"
        assert product_list[1].gubun == "1+1"

    def test_one_one_price_setting_product_not_found(
            self,
            client: TestClient,
            mock_product_one_one_price_usecase,
            invalid_product_request_data
        ):
        """1+1 가격 설정 - 상품을 찾을 수 없는 경우 테스트"""
        
        # Mock ProductOneOnePriceUsecase가 ValueError 발생
        mock_calculate = mock_product_one_one_price_usecase.calculate_and_save_one_one_price
        mock_calculate.side_effect = ValueError("상품을 찾을 수 없습니다.")
        
        # Mock calculate_and_save_one_one_price 메서드가 ValueError 발생
        mock_calculate.side_effect = ValueError("상품을 찾을 수 없습니다.")
        
        # When: API 요청 실행
        response = client.post("/api/v1/one-one-price/", json=invalid_product_request_data)
        
        # Then: 응답 검증
        assert response.status_code == 404
        response_data = response.json()
        assert response_data["detail"] == "상품을 찾을 수 없습니다."

    def test_one_one_price_setting_price_range_error(
            self,
            client: TestClient,
            mock_product_one_one_price_usecase,
            sample_one_one_price_request_data

        ):
        """1+1 가격 설정 - 가격 범위 오류 테스트"""
        
        # Mock ProductOneOnePriceUsecase가 DBAPIError 발생
        mock_calculate = mock_product_one_one_price_usecase.calculate_and_save_one_one_price
        mock_calculate.side_effect = DBAPIError("integer out of range", None, None)
            
        # When: API 요청 실행
        response = client.post("/api/v1/one-one-price/", json=sample_one_one_price_request_data)
        
        # Then: 응답 검증
        assert response.status_code == 400
        response_data = response.json()
        assert response_data["detail"] == "원본 상품 가격이 너무 커서 계산할 수 없습니다."

    def test_one_one_price_bulk_setting_db_error(
            self,
            client: TestClient,
            mock_product_one_one_price_usecase,
            sample_one_one_price_bulk_request_data
        ):
        """1+1 가격 대량 설정 - 데이터베이스 오류 테스트"""
        
        # Mock ProductOneOnePriceUsecase가 DBAPIError 발생
        mock_calculate_bulk = mock_product_one_one_price_usecase.calculate_and_save_one_one_prices_bulk
        mock_calculate_bulk.side_effect = DBAPIError("integer out of range", None, None)
            
        # When: API 요청 실행
        response = client.post("/api/v1/one-one-price/bulk", json=sample_one_one_price_bulk_request_data)
        
        # Then: 응답 검증
        assert response.status_code == 400
        response_data = response.json()
        assert response_data["detail"] == "원본 상품 가격이 너무 커서 계산할 수 없습니다."

    def test_one_one_price_bulk_setting_partial_success(
            self,
            client: TestClient,
            mock_product_one_one_price_usecase,
            sample_one_one_price_bulk_request_data_partial_success
        ):
        """1+1 가격 대량 설정 - 부분적 성공 테스트"""
        
        # Mock ProductOneOnePriceUsecase
        mock_calculate_bulk = mock_product_one_one_price_usecase.calculate_and_save_one_one_prices_bulk
        
        # Mock DTO 생성 (성공한 상품들만)
        mock_dto1 = OneOnePriceDto(
            test_product_raw_data_id=2,
            product_nm="테스트상품2",
            compayny_goods_cd="GOODS002",
            standard_price=Decimal("14000"),
            one_one_price=Decimal("28900"),
            shop0007=Decimal("33900"),  # group_115
            shop0042=Decimal("33900"),  # group_115
            shop0087=Decimal("33900"),  # group_115
            shop0094=Decimal("33900"),  # group_115
            shop0121=Decimal("33900"),  # group_115
            shop0129=Decimal("33900"),  # group_115
            shop0154=Decimal("33900"),  # group_115
            shop0650=Decimal("33900"),  # group_115
            shop0029=Decimal("30900"),  # group_105
            shop0189=Decimal("30900"),  # group_105
            shop0322=Decimal("30900"),  # group_105
            shop0444=Decimal("30900"),  # group_105
            shop0100=Decimal("30900"),  # group_105
            shop0298=Decimal("30900"),  # group_105
            shop0372=Decimal("30900"),  # group_105
            shop0381=Decimal("28900"),  # group_same
            shop0416=Decimal("28900"),  # group_same
            shop0449=Decimal("28900"),  # group_same
            shop0498=Decimal("28900"),  # group_same
            shop0583=Decimal("28900"),  # group_same
            shop0587=Decimal("28900"),  # group_same
            shop0661=Decimal("28900"),  # group_same
            shop0075=Decimal("28900"),  # group_same
            shop0319=Decimal("28900"),  # group_same
            shop0365=Decimal("28900"),  # group_same
            shop0387=Decimal("28900"),  # group_same
            shop0055=Decimal("29000"),  # group_plus100
            shop0067=Decimal("29000"),  # group_plus100
            shop0068=Decimal("29000"),  # group_plus100
            shop0273=Decimal("29000"),  # group_plus100
            shop0464=Decimal("29000")   # group_plus100
        )
        
        mock_dto2 = OneOnePriceDto(
            test_product_raw_data_id=5,
            product_nm="테스트상품5",
            compayny_goods_cd="GOODS005",
            standard_price=Decimal("17000"),
            one_one_price=Decimal("34900"),
            shop0007=Decimal("40900"),  # group_115
            shop0042=Decimal("40900"),  # group_115
            shop0087=Decimal("40900"),  # group_115
            shop0094=Decimal("40900"),  # group_115
            shop0121=Decimal("40900"),  # group_115
            shop0129=Decimal("40900"),  # group_115
            shop0154=Decimal("40900"),  # group_115
            shop0650=Decimal("40900"),  # group_115
            shop0029=Decimal("37900"),  # group_105
            shop0189=Decimal("37900"),  # group_105
            shop0322=Decimal("37900"),  # group_105
            shop0444=Decimal("37900"),  # group_105
            shop0100=Decimal("37900"),  # group_105
            shop0298=Decimal("37900"),  # group_105
            shop0372=Decimal("37900"),  # group_105
            shop0381=Decimal("34900"),  # group_same
            shop0416=Decimal("34900"),  # group_same
            shop0449=Decimal("34900"),  # group_same
            shop0498=Decimal("34900"),  # group_same
            shop0583=Decimal("34900"),  # group_same
            shop0587=Decimal("34900"),  # group_same
            shop0661=Decimal("34900"),  # group_same
            shop0075=Decimal("34900"),  # group_same
            shop0319=Decimal("34900"),  # group_same
            shop0365=Decimal("34900"),  # group_same
            shop0387=Decimal("34900"),  # group_same
            shop0055=Decimal("35000"),  # group_plus100
            shop0067=Decimal("35000"),  # group_plus100
            shop0068=Decimal("35000"),  # group_plus100
            shop0273=Decimal("35000"),  # group_plus100
            shop0464=Decimal("35000")   # group_plus100
        )
        
        mock_bulk_dto = OneOnePriceBulkDto(
            success_count=2,
            error_count=1,
            created_product_nm=["테스트상품2", "테스트상품5"],
            errors=["잘못된 상품을 찾을 수 없습니다"],
            success_data=[mock_dto1, mock_dto2]
        )
        
        mock_calculate_bulk.return_value = mock_bulk_dto
        
        # When: API 요청 실행
        response = client.post("/api/v1/one-one-price/bulk", json=sample_one_one_price_bulk_request_data_partial_success)
        
        # Then: 응답 검증
        assert response.status_code == 200
        response_data = response.json()
        
        # 응답 구조 검증
        assert "success_count" in response_data
        assert "error_count" in response_data
        assert "created_product_nm" in response_data
        assert "errors" in response_data
        assert "success_data" in response_data
        
        # Mock 데이터와 일치하는지 확인
        assert response_data["success_count"] == 2
        assert response_data["error_count"] == 1
        assert response_data["created_product_nm"] == ["테스트상품2", "테스트상품5"]
        assert response_data["errors"] == ["잘못된 상품을 찾을 수 없습니다"]
        assert len(response_data["success_data"]) == 2
        
        # Mock 메서드가 올바른 파라미터로 호출되었는지 확인
        # API에서 JSON을 받아서 Pydantic 모델로 변환하므로 OneOnePriceCreate 객체 리스트가 전달됨
        call_args = mock_calculate_bulk.call_args
        assert call_args is not None
        assert "product_nm_and_gubun_list" in call_args.kwargs
        product_list = call_args.kwargs["product_nm_and_gubun_list"]
        assert len(product_list) == 3
        assert product_list[0].product_nm == "테스트상품2"
        assert product_list[0].gubun == "1+1"
        assert product_list[1].product_nm == "테스트상품5"
        assert product_list[1].gubun == "1+1"
        assert product_list[2].product_nm == "잘못된 상품"
        assert product_list[2].gubun == "잘못된 구분"