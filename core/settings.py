from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):

    # SabangNet
    SABANG_COMPANY_ID: Optional[str] = None
    SABANG_AUTH_KEY: Optional[str] = None
    SABANG_ADMIN_URL: Optional[str] = None
    SABANG_SEND_GOODS_CD_RT: str = ""
    SABANG_RESULT_TYPE: str = "XML"

    # MinIO
    MINIO_ROOT_USER: Optional[str] = None
    MINIO_ROOT_PASSWORD: Optional[str] = None
    MINIO_ACCESS_KEY: Optional[str] = None
    MINIO_SECRET_KEY: Optional[str] = None
    MINIO_ENDPOINT: Optional[str] = None
    MINIO_BUCKET_NAME: Optional[str] = None
    MINIO_USE_SSL: Optional[str] = None
    MINIO_PORT: Optional[str] = None

    # DB
    DB_HOST: Optional[str] = None
    DB_PORT: Optional[str] = None
    DB_NAME: Optional[str] = None
    DB_USER: Optional[str] = None
    DB_PASSWORD: Optional[str] = None
    DB_SSLMODE: Optional[str] = None

    # N8N
    N8N_TEST: Optional[str] = None
    N8N_WEBHOOK_BASE_URL: Optional[str] = None
    N8N_WEBHOOK_PATH: Optional[str] = None

    # FastAPI
    FASTAPI_HOST: Optional[str] = None
    FASTAPI_PORT: Optional[str] = None

    class Config:
        env_file = ".env"


SETTINGS = Settings()
