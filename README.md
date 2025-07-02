# 1. 가상환경 생성
Python 3.12.*

python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는 venv\Scripts\activate  # Windows

# 2. 의존성 설치
pip3 install -r requirements.txt

# 3. 환경변수 설정
cp .env.example .env
# .env 파일에 실제 값 입력

# 4. 실행
python app.py [command]
python app.py --help          # Show help
python app.py mall-list       # List malls
python app.py order-list      # List orders

# 사방넷 쇼핑몰 코드 조회 API

사방넷의 쇼핑몰 코드 조회 API를 Python으로 구현한 클라이언트입니다.

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

# 의존성 설치

```bash
pip3 install -r requirements.txt
```

## CLI 명령어

이 프로그램은 Typer를 사용한 CLI 인터페이스를 제공합니다:

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
└─────── excel
└─────── sample
└─────── xml
└── logs                 # 작업용 log 파일 관리
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
  python app.py test-db-write "테스트값"

- ReceiveOrder 모델 조회 테스트:  
  python app.py test-receive-order

- 수집된 주문 DB에 저장:  
  python app.py create-order

- 상품 등록:  
  python app.py create-product

- Excel 파일에서 상품 등록 데이터 가져오기:  
  python app.py import-product-registration-excel "./경로/파일.xlsx" --sheet-name "Sheet1"

- 상품 등록 Data 기반으로 excel 수식 To Method 상품 등록 대량 등록 To DB
  python app.py generate-product-code-data

```bash
# .env file
# 사방넷 API 설정
SABANG_COMPANY_ID=
SABANG_AUTH_KEY=
SABANG_ADMIN_URL=

MINIO_ROOT_USER=
MINIO_ROOT_PASSWORD=
MINIO_ACCESS_KEY=
MINIO_SECRET_KEY=
MINIO_ENDPOINT=
MINIO_BUCKET_NAME=
MINIO_USE_SSL=
MINIO_PORT=

DB_HOST=
DB_PORT=
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_SSLMODE=
DB_TEST_COLUMN=
DB_TEST_TABLE=

N8N_TEST=
N8N_WEBHOOK_BASE_URL=
N8N_WEBHOOK_PATH=
```
