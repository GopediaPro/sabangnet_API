# 1. 가상환경 생성
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는 venv\Scripts\activate  # Windows

# 2. 의존성 설치
pip3 install -r requirements.txt

# 3. 환경변수 설정
cp .env.example .env
# .env 파일에 실제 값 입력

# 4. 실행
python sabangnet_mall_api.py

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
#  실행
python app.py

### 2. 의존성 설치

```bash
pip3 install -r requirements.txt
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

## 사용 방법

### 1. 기본 사용법

```bash
python app.py
```

프로그램 실행 후 XML 파일의 URL을 입력하면 쇼핑몰 목록을 조회할 수 있습니다.

### 2. 프로그래밍 방식 사용

```python
from sabangnet_mall_api import SabangNetMallAPI

# API 클라이언트 생성
api = SabangNetMallAPI()

# 요청 XML 생성
xml_content = api.create_request_xml()

# XML 파일로 저장
api.save_xml_to_file(xml_content, 'your_xml_file.xml')

# 쇼핑몰 목록 조회 (XML URL 필요)
mall_list = api.get_mall_list_via_url('http://your-domain.com/your-xml-file.xml')

# 결과 출력
api.display_mall_list(mall_list)
```

## 주요 기능

- **환경변수 관리**: 민감한 정보(ID, 인증키)를 환경변수로 안전하게 관리
- **XML 생성**: 사방넷 API 요청용 XML 자동 생성
- **API 통신**: 사방넷과의 HTTP 통신 처리
- **응답 파싱**: XML 응답을 Python 객체로 변환
- **에러 처리**: 상세한 로깅과 예외 처리

## 파일 구조

```
.
├── sabangnet_mall_api.py    # 메인 API 클라이언트
├── requirements.txt         # Python 의존성
├── .env.example            # 환경변수 예시
├── .env                    # 실제 환경변수 (생성 필요)
└── README.md              # 이 파일
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
