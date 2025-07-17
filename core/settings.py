from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):

    # SabangNet
    SABANG_COMPANY_ID: Optional[str] = None
    SABANG_AUTH_KEY: Optional[str] = None
    SABANG_ADMIN_URL: Optional[str] = None
    SABANG_SEND_GOODS_CD_RT: Optional[str] = ""
    SABANG_RESULT_TYPE: Optional[str] = "XML"

    # MinIO
    MINIO_ROOT_USER: Optional[str] = None
    MINIO_ROOT_PASSWORD: Optional[str] = None
    MINIO_ACCESS_KEY: Optional[str] = None
    MINIO_SECRET_KEY: Optional[str] = None
    MINIO_ENDPOINT: Optional[str] = None
    MINIO_BUCKET_NAME: Optional[str] = None
    MINIO_USE_SSL: Optional[bool] = None
    MINIO_PORT: Optional[int] = None

    # DB
    DB_HOST: Optional[str] = None
    DB_PORT: Optional[int] = None
    DB_NAME: Optional[str] = None
    DB_USER: Optional[str] = None
    DB_PASSWORD: Optional[str] = None
    DB_SSLMODE: Optional[str] = None
    DB_TEST_TABLE: Optional[str] = None
    DB_TEST_COLUMN: Optional[str] = None

    # N8N
    N8N_WEBHOOK_BASE_URL: Optional[str] = None
    N8N_WEBHOOK_PATH: Optional[str] = None

    # FastAPI
    FASTAPI_HOST: Optional[str] = None
    FASTAPI_PORT: Optional[int] = None

    # Test Mode
    CONPANY_GOODS_CD_TEST_MODE: Optional[bool] = True

    DEPLOY_ENV: Optional[bool] = None

    class Config:
        env_file = ".env"


SETTINGS = Settings()
