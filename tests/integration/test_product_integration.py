from decimal import Decimal
from datetime import datetime
from fastapi.testclient import TestClient
from fastapi.responses import StreamingResponse
from schemas.product.product_raw_data_dto import ProductRawDataDto
from schemas.product.modified_product_dto import ModifiedProductDataDto


pytest_plugins = ["tests.fixtures.product.conftest"]


class TestProductIntegration:
    """Product 엔드포인트 통합 테스트"""

    # test_db_to_xml_sabangnet_request_with_test_mode_validation 삭제 