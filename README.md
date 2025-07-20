테스트관련 소스는 ~/project/sabangnet_API/test_macro/cmp.py 만 있으면 되므로 이것만 다운 받아서 사용하세요.
아래는 실행방법이고, 실행 Command 아래쪽에는 엑셀과 리브레오피스에서 시트 복사하는 방법 설명입니다.

cmp.py 수정한 다음 사용하시면 되십니다.<br/>
  Line 182 : excel_file : 확인할 파일명<br/>
  Line 183 : compare_selected_sheet_pairs의  2번째 파라미터 (비교할 시트쌍의 개수)<p/>
실행:<br/>
  python cmp.py [/filepath/compare_excel_filename.xlsx] <p/>

엑셀 파일 1개에 파이선시트[시트1, 시트2, 시트3], 매크로 시트[시트1_m, 시트2_m, 시트3_m) 순서로 엑셀 통합(시트 선택한 다음 시트복사 하시면 됩니다.)
시트 복사 방법
    1. 복사할 원천 엑셀과 대상 엑셀을 실행해서 함께 열어둡니다.
      <img width="1551" height="727" alt="image" src="https://github.com/user-attachments/assets/959ba2af-2484-4c00-886c-0a9190e6c55e" />
    2. 원천엑셀의 복사할 시트를 선택합니다. Ctrl을 누른 상태로 시트의 이름을 선택하면 한꺼번에 여러 시트를 선택할 수 있습니다.
       <img width="645" height="275" alt="image" src="https://github.com/user-attachments/assets/2416bf5f-a639-4cbb-9add-aea135d39375" />
    3. 선택한 시트를 오른쪽 클립합니다.
      <img width="463" height="382" alt="image" src="https://github.com/user-attachments/assets/d055510d-ff00-4381-8647-00cdcfbbb38b" />
    4. 메뉴에서 이동/복사 선택
    5. 통합대상문서 선택
    6. 끝으로 이동 선택
    7. 복사본 만들기 선택
    8. 확인 => 여기까지 완료하면 시트가 복사된 것을 확인할 수 있습니다.

엑셀이 없으면 리브레오피스를 사용하셔도 됩니다. 엑셀은 소스를 선택해서 대상에 붙여넣기 방식이지만 리브레는 현재 파일에 대상파일을 읽어오는 방식입니다.
    1. 복사본을 가진 파일을 열어둔다.  ex) libreoffice target.xlsx
    2. 메뉴 시트(S) > 파일에서 시트 삽입
      <img width="538" height="500" alt="image" src="https://github.com/user-attachments/assets/d63416a2-f87f-4ef4-a942-b8ca88929d45" />
    3. 읽어올 파일 선택 => 열기
      <img width="782" height="246" alt="image" src="https://github.com/user-attachments/assets/42eda275-0579-45e1-abf0-0f263ffffd4c" />
    4. 현재 시트 뒤에 선택
       <img width="669" height="540" alt="image" src="https://github.com/user-attachments/assets/ceb76acb-e012-4fb5-87ab-57bdf840f756" />
    5. 아래쪽의 파일에서 작성에서 읽어올 시트 선택(shift를 사용하면 여러개 선택 가능)
       <img width="663" height="538" alt="image" src="https://github.com/user-attachments/assets/18f1a210-cf91-4f75-aa36-7a1dfa6c449c" />
    6. 확인하면  => 여기까지 완료하면 시트가 복사된 것을 확인할 수 있습니다.


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
# 개발환경 명령어 (개인정보 마스킹용)
export DEPLOY_ENV=development

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
```
