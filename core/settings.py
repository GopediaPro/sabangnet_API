from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    # SabangNet
    SABANG_COMPANY_ID: str
    SABANG_AUTH_KEY: str
    SABANG_ADMIN_URL: str
    SABANG_SEND_GOODS_CD_RT: str = ""
    SABANG_RESULT_TYPE: str = "XML"

    # MinIO
    MINIO_ROOT_USER: str
    MINIO_ROOT_PASSWORD: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_ENDPOINT: str
    MINIO_BUCKET_NAME: str
    MINIO_USE_SSL: str
    MINIO_PORT: str

    # DB
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_SSLMODE: str

    class Config:
        env_file = ".env"


SETTINGS = Settings()
