## 설치 및 설정

### 1. 가상환경 생성 및 활성화

```bash
# 가상환경 생성
python3 -m venv venv

# 가상환경 활성화 (Linux/Mac)
source venv/bin/activate

# 가상환경 활성화 (Windows)
venv\Scripts\activate
```
# ssl 오류 해결용 명령어
export OPENSSL_CONF=./config/openssl.cnf
# 개발환경 명령어 (개인정보 마스킹용)
export DEPLOY_ENV=development
export DEPLOY_ENV=production

# 의존성 설치

```bash
pip3 install -r requirements.txt
```

## CLI 명령어

### FastAPI 활용
```bash
uvicorn main:app --port 8008 --reload

# web에서 
http://localhost:8008/docs

# 실행하고 싶은 엔드포인트 ->  Try it out → Execute (request 값 필요 시 입력)
```

# push 전 pytest 통과 확인
```bash
python -m pytest tests/ --verbose --tb=short --maxfail=3 --disable-warnings
```

### 이 프로그램은 Typer를 사용한 CLI 인터페이스를 제공합니다:

```bash
# 도움말 보기
python app.py --help

# 쇼핑몰 목록 조회
python app.py mall-list

# 주문 목록 조회
python app.py order-list
```

각 명령어의 도움말을 보려면:
```bash
python app.py mall-list --help
python app.py order-list --help
```

### 3. 환경변수 설정

`.env.example` 파일을 `.env`로 복사하고 실제 값을 입력합니다:

```bash
cp .env.example .env
```

`.env` 파일을 편집하여 실제 값을 입력:

```bash
SABANG_COMPANY_ID=실제_회사_아이디
SABANG_AUTH_KEY=실제_인증키
SABANG_ADMIN_URL=https://sbadmin실제번호.sabangnet.co.kr
```

## 주요 기능

- **CLI 인터페이스**: Typer를 활용한 직관적인 명령행 인터페이스
- **환경변수 관리**: 민감한 정보(ID, 인증키)를 환경변수로 안전하게 관리
- **XML 생성**: 사방넷 API 요청용 XML 자동 생성
- **API 통신**: 사방넷과의 HTTP 통신 처리
- **응답 파싱**: XML 응답을 Python 객체로 변환
- **에러 처리**: 상세한 로깅과 예외 처리

## 로깅

- **로거 사용 방법**: 스크립트 최상단에 logger 객체를 불러와서 씁니다.

```
from utils.sabangnet_logger import get_logger

logger = get_logger(__name__)

# 아래중에 선택
logger.debug(내용)
logger.info(내용)
logger.warning(내용)
logger.error(내용)
logger.critical(내용)
```

- **DEBUG**: 디버깅용 상세정보
- **INFO**: 일반적인 정보
- **WARNING**: 경고 (문제는 아니지만 주의)
- **ERROR**: 에러 발생
- **CRITICAL**: 치명적인 에러

## 파일 구조

```
.
├── app.py                  # CLI 애플리케이션 메인 파일
├── controller/            # 컨트롤러 모듈
├── requirements.txt       # Python 의존성
├── .env.example          # 환경변수 예시
├── .env                  # 실제 환경변수 (생성 필요)
└── README.md            # 이 파일
└── files                # 작업용 files
└─────── excel
└─────── json
└─────── logs
└─────── xml
```

## 주의사항

1. **인증키 발급**: 사방넷에서 인증키를 미리 발급받아야 합니다.
2. **XML 파일 접근**: XML 파일은 웹에서 접근 가능한 URL이어야 합니다.
3. **인코딩**: XML 파일은 EUC-KR 인코딩을 사용합니다.
4. **보안**: `.env` 파일은 절대 git에 커밋하지 마세요.

## 트러블슈팅

### 인증 오류
- `SABANG_COMPANY_ID`와 `SABANG_AUTH_KEY`가 올바른지 확인
- 사방넷에서 발급한 인증키가 유효한지 확인

### XML 파일 접근 오류
- XML URL이 웹에서 접근 가능한지 확인
- XML 파일의 인코딩이 EUC-KR인지 확인

### 파싱 오류
- XML 파일 형식이 사방넷 API 스펙에 맞는지 확인

- 응답 XML의 구조가 예상과 같은지 확인

# 주요 CLI 명령어 요약

- 쇼핑몰 목록 조회:  
  python app.py mall-list

- 주문 목록 조회:  
  python app.py order-list

- DB 연결 테스트:  
  python app.py test-db-connection

- DB Write 테스트:  
  python app.py test-db-write-command "테스트값"

- ReceiveOrders 모델 조회 테스트:  
  python app.py test-receive-order

- 수집된 주문 DB에 저장:  
  python app.py create-order

- 상품 등록:  
  python app.py request-product-create 엑셀파일이름 엑셀시트이름

- Excel 파일에서 상품 등록 데이터 가져오기:  
  python app.py import-product-registration-excel "./경로/파일.xlsx" --sheet-name "Sheet1"

- 주문 목록을 엑셀로 변환:
  python app.py create-order-xlsx

- 테스트 ERP 매크로 실행:
  python app.py test-erp-macro

- 상품 등록 Data 기반으로 excel 수식 To Method 상품 등록 대량 등록 To DB:
  python app.py generate-product-code-data

- 특정 상품 쇼핑몰별 1+1 가격 계산:
  python app.py calculate-one-one-price 상품원본모델명

- FastAPI 서버 실행:
  python app.py start-server

- pytest 테스트 실행:
  python -m pytest tests/ --verbose --tb=short --maxfail=3 --disable-warnings

- pytest 테스트 실행 (HTML 리포트 포함):
  python -m pytest tests/ --verbose --tb=short --maxfail=3 --disable-warnings --html=test-report.html --self-contained-html

- pytest 테스트 실행 (커버리지 포함):
  python -m pytest tests/ --verbose --tb=short --maxfail=3 --disable-warnings --cov=tests --cov-report=html:coverage-report --cov-report=xml:coverage.xml

```bash
# .env file
# SABANGNET 연결
SABANG_COMPANY_ID=
SABANG_AUTH_KEY=
SABANG_ADMIN_URL=
# MINIO 연결
MINIO_ROOT_USER=
MINIO_ROOT_PASSWORD=
MINIO_ACCESS_KEY=
MINIO_SECRET_KEY=
MINIO_ENDPOINT=
MINIO_BUCKET_NAME=
MINIO_USE_SSL=
MINIO_PORT=
# DB 연결
DB_HOST=
DB_PORT=
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_SSLMODE=
# n8n 웹훅 테스트 URI
N8N_WEBHOOK_BASE_URL=
N8N_WEBHOOK_PATH=
# uvicorn
FASTAPI_HOST=
FASTAPI_PORT=
FASTAPI_RELOAD=
# 엑셀 테스트 환경
CONPANY_GOODS_CD_TEST_MODE=
# 배포환경 감지 변수
DEPLOY_ENV=
# ecount 이카운트 API 연동관련
ECOUNT_ID=
ECOUNT_API=
ECOUNT_ZONE=
ECOUNT_DOMAIN=
# hanjin API 연동관련
HANJIN_API=
HANJIN_CLIENT_ID=
HANJIN_API_SECRET_KEY=
```

## 기술 스택

| 구분            | 사용 기술 (버전)                                 |
|-----------------|-------------------------------------------------|
| Python          | Python >= 3.12                                  |
| Web Framework   | FastAPI (0.115.12), Starlette (0.46.2), Uvicorn (0.34.3) |
| ORM/DB          | SQLAlchemy (2.0.41), asyncpg (0.30.0)           |
| 데이터 처리     | Pandas (2.3.0), lxml (5.4.0), openpyxl (3.1.5), xlsxwriter |
| 환경설정        | python-dotenv (1.1.0), pydantic (2.11.7), pydantic-settings (2.9.1) |
| HTTP 클라이언트 | Requests (2.32.4), httpx, aiohttp (>=3.8.0)     |
| 파일 업로드     | python-multipart (0.0.20)                       |
| 오브젝트 스토리지| Minio (7.2.15)                                  |
| CLI             | Typer (0.16.0)                                  |
| 테스트          | pytest, pytest-html, pytest-xdist, pytest-cov, pytest-asyncio |
| 기타            | 없음                                            |

## Alembic (DB 마이그레이션) 적용 및 사용법

### 1. Alembic 설치

```bash
pip install alembic
```

### 2. Alembic 환경설정
- alembic.ini의 DB URL은 비워두고, alembic/env.py에서 환경변수 또는 settings를 통해 동적으로 DB URL을 주입합니다.
- alembic/env.py에서 모든 모델이 Base.metadata에 등록되도록 `import models`를 반드시 추가합니다.
- 마이그레이션 파일(예: alembic/versions/...)은 반드시 git에 커밋합니다.

### 3. Alembic 기본 명령어

```bash
# 마이그레이션 파일 생성 (모델 변경 후)
alembic revision --autogenerate -m "설명 메시지"

# DB에 마이그레이션 적용
alembic upgrade head

# DB를 특정 리비전으로 되돌리기 (주의: 데이터 손실 가능)
alembic downgrade <revision_id>

# DB와 마이그레이션 버전 동기화만 (실제 구조 변경 X, 운영 DB에 적용 시)
alembic stamp head
```

### 4. Alembic 적용 워크플로우
1. 모델(Base) 변경 (필드 추가/삭제/수정 등)
2. `alembic revision --autogenerate -m "설명"` 으로 마이그레이션 파일 생성
3. 마이그레이션 파일을 검토/수정 (기본값, 데이터 변환 등 필요시)
4. `alembic upgrade head`로 실제 DB에 적용

### 5. 테스트 환경에서 Alembic 적용
- pytest 실행 시, `tests/conftest.py`에서 자동으로 `alembic upgrade head`가 실행되어 테스트용 DB가 항상 최신 스키마로 유지됩니다.
- 별도의 테이블 생성(create_tables) 코드는 사용하지 않습니다.

### 6. 주의사항
- alembic/versions/ 폴더와 마이그레이션 파일은 반드시 git에 포함해야 합니다.
- .env 파일에 DB 정보가 올바르게 입력되어 있어야 합니다.
- 운영 DB에 적용 전에는 반드시 백업을 권장합니다.
- NOT NULL 컬럼 추가, UNIQUE 제약 추가 등은 기존 데이터와 충돌이 없는지 반드시 확인하세요.

---
