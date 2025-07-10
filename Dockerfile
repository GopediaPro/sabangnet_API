FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# 코드 품질 도구 설치 (이미 requirements.txt에 있다면 생략)
# RUN pip install flake8 black isort mypy pytest

# 린트, 타입, 테스트 체크 (실패 시 빌드 중단)
# RUN flake8 . && black --check . && isort --check-only . && mypy . && pytest --maxfail=1 --disable-warnings

COPY . .

# 임시 .env 파일 생성
RUN echo "SABANG_COMPANY_ID=\n\
SABANG_AUTH_KEY=\n\
SABANG_ADMIN_URL=\n\
MINIO_ROOT_USER=\n\
MINIO_ROOT_PASSWORD=\n\
MINIO_ACCESS_KEY=\n\
MINIO_SECRET_KEY=\n\
MINIO_ENDPOINT=\n\
MINIO_BUCKET_NAME=\n\
MINIO_USE_SSL=\n\
MINIO_PORT=\n\
DB_HOST=\n\
DB_PORT=\n\
DB_NAME=\n\
DB_USER=\n\
DB_PASSWORD=\n\
DB_SSLMODE=\n\
DB_TEST_COLUMN=\n\
DB_TEST_TABLE=\n\
FASTAPI_HOST=api.lyckabc.xyz\n\
FASTAPI_PORT=8008\n\
N8N_WEBHOOK_BASE_URL=\n\
N8N_WEBHOOK_PATH=\n\
CONPANY_GOODS_CD_TEST_MODE=\n" > .env

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8008", "--env-file", ".env"]
