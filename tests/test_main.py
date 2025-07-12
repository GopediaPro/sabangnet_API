"""
메인 앱 테스트
"""
import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from utils.sabangnet_logger import get_logger


logger = get_logger(__name__)


@pytest.mark.unit
def test_app_creation(test_app):
    """FastAPI 앱 생성 테스트"""

    try:
        assert test_app is not None
        assert test_app.title == "SabangNet API <-> n8n 연결 테스트"
        assert test_app.version == "0.1.2"
        logger.info("FastAPI 앱 생성 테스트 완료")
    except Exception as e:
        logger.error(f"FastAPI 앱 생성 테스트 실패: {e}")
        raise e


@pytest.mark.api
def test_root_endpoint(client: TestClient):
    """루트 테스트"""

    try:
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == "FastAPI 메인페이지 입니다."
        logger.info("루트 엔드포인트 테스트 완료")
    except Exception as e:
        logger.error(f"루트 엔드포인트 테스트 실패: {e}")
        raise e


@pytest.mark.api
def test_docs_endpoint(client: TestClient):
    """Swagger UI 테스트"""
    try:
        response = client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        logger.info("Swagger UI 엔드포인트 테스트 완료")
    except Exception as e:
        logger.error(f"Swagger UI 엔드포인트 테스트 실패: {e}")
        raise e


@pytest.mark.api
def test_redoc_endpoint(client: TestClient):
    """ReDoc 테스트"""
    try:
        response = client.get("/redoc")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        logger.info("ReDoc 엔드포인트 테스트 완료")
    except Exception as e:
        logger.error(f"ReDoc 엔드포인트 테스트 실패: {e}")
        raise e


@pytest.mark.api
def test_cors_middleware(client: TestClient):
    """CORS 미들웨어 테스트"""
    try:
        headers = {
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Content-Type"
        }
    
        response = client.options("/", headers=headers)
        
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers
        # allow_credentials=True일 때는 Origin 헤더 값이 그대로 반환된다고 함
        # assert response.headers["access-control-allow-origin"] == "*"
        assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
        assert "access-control-allow-credentials" in response.headers
        assert response.headers["access-control-allow-credentials"] == "true"

        logger.info("CORS 미들웨어 테스트 완료")
    except Exception as e:
        logger.error(f"CORS 미들웨어 테스트 실패: {e}")
        raise e


@pytest.mark.api
def test_api_prefix_endpoints(client: TestClient):
    """API 프리픽스 엔드포인트 존재 확인"""
    # OpenAPI 스키마에서 사용 가능한 경로 확인

    try:
        response = client.get("/openapi.json")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
    
        schema: dict = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert schema["info"]["title"] == "SabangNet API <-> n8n 연결 테스트"
        assert schema["info"]["version"] == "0.1.2"

        paths: dict = schema.get("paths", {})
        
        api_paths = []
        api_v1_paths = []
        not_api_paths = []
        for path in paths.keys():
            path: str
            if path.startswith("/api"):
                if path.startswith("/api/v1"):
                    api_v1_paths.append(path)
                else:
                    api_paths.append(path)
            else:
                not_api_paths.append(path)
        
        logger.info(f"api_paths={api_paths}")
        logger.info(f"api_v1_paths={api_v1_paths}")
        logger.info(f"not_api_paths={not_api_paths}")
        
        assert len(api_v1_paths) > 0 and len(api_paths) > 0, "API 엔드포인트가 존재하지 않스비낟"
    except Exception as e:
        logger.error(f"API 프리픽스 엔드포인트 존재 확인 테스트 실패: {e}")
        raise e