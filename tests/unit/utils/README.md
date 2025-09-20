# ProductTextProcessor 단위 테스트

## 개요

`ProductTextProcessor`는 제품명 텍스트를 처리하여 중복 제품을 통합하고 수량을 계산하는 유틸리티 클래스입니다.

## 주요 기능

- **중복 제품 통합**: "+" 구분자로 분리된 제품명에서 중복 제품을 찾아 수량을 합산
- **특수 조건 처리**: 사은품, 증정품 등 특정 키워드가 포함된 제품 제외
- **수량 계산**: 각 제품의 수량을 추출하고 합산
- **다중 제품 감지**: 여러 제품이 포함된 제품명인지 확인

## 테스트 구조

```
tests/unit/utils/
├── __init__.py
├── test_product_text_processor.py    # 메인 테스트 파일
├── run_product_text_tests.py         # 테스트 실행 스크립트
└── README.md                         # 이 파일
```

## 테스트 클래스

### 1. TestProductTextProcessor
- 기본 기능 테스트
- 중복 제품 통합 테스트
- 제외 키워드 처리 테스트

### 2. TestConvenienceFunctions
- 편의 함수들 테스트

### 3. TestEdgeCases
- 엣지 케이스 테스트
- 공백 처리, 특수 문자 등

### 4. TestPerformance
- 성능 테스트
- 큰 입력 데이터 처리

### 5. TestParameterized
- 파라미터화된 테스트
- 다양한 시나리오 자동 테스트

## 사용 예시

### 기본 사용법

```python
from utils.product_text_processor import ProductTextProcessor

processor = ProductTextProcessor()

# 중복 제품 통합
result = processor.process_product_text("OMS-703(BL) + OMS-703(BL)")
# 결과: "OMS-703(BL) 2개"

# 혼합 제품 처리
result = processor.process_product_text("OSA-146 + OSA-D717 + OSA-146")
# 결과: "OSA-146 2개 + OSA-D717"
```

### 편의 함수 사용

```python
from utils.product_text_processor import process_product_text, get_product_quantity_count

# 제품명 처리
result = process_product_text("제품A + 제품A")
# 결과: "제품A 2개"

# 수량 계산
quantity = get_product_quantity_count("제품A 2개 + 제품B 3개")
# 결과: 5
```

## 테스트 실행

### 전체 테스트 실행

```bash
# pytest 사용
pytest tests/unit/utils/test_product_text_processor.py -v

# 또는 실행 스크립트 사용
python tests/unit/utils/run_product_text_tests.py
```

### 특정 테스트 실행

```bash
# 특정 테스트 클래스 실행
pytest tests/unit/utils/test_product_text_processor.py::TestProductTextProcessor -v

# 특정 테스트 메서드 실행
pytest tests/unit/utils/test_product_text_processor.py::TestProductTextProcessor::test_basic_duplicate_merge -v

# 키워드로 테스트 필터링
pytest tests/unit/utils/test_product_text_processor.py -k "duplicate" -v
```

### 실행 스크립트 옵션

```bash
# 전체 테스트 실행
python tests/unit/utils/run_product_text_tests.py

# 특정 테스트만 실행
python tests/unit/utils/run_product_text_tests.py --test "duplicate"
```

## 테스트 케이스 예시

### 1. 기본 중복 통합
- **입력**: `"OMS-703(BL) + OMS-703(BL)"`
- **예상 결과**: `"OMS-703(BL) 2개"`

### 2. 혼합 제품 처리
- **입력**: `"OSA-146 + OSA-D717 + OSA-146"`
- **예상 결과**: `"OSA-146 2개 + OSA-D717"`

### 3. 수량이 명시된 제품
- **입력**: `"제품A 3개 + 제품B 2개 + 제품A 1개"`
- **예상 결과**: `"제품A 4개 + 제품B 2개"`

### 4. 제외 키워드 처리
- **입력**: `"제품A + [사은품]제품B + 제품C"`
- **예상 결과**: `"제품A + 제품C"`

## 확장성

이 테스트 구조는 향후 다른 수식 관련 유틸리티들의 단위 테스트를 추가하기에 적합합니다:

- `tests/unit/utils/test_math_utils.py` - 수학 계산 유틸리티
- `tests/unit/utils/test_formula_parser.py` - 수식 파서
- `tests/unit/utils/test_calculation_engine.py` - 계산 엔진

## 주의사항

1. 테스트 실행 전에 프로젝트 루트 디렉토리가 Python 경로에 포함되어야 합니다.
2. pytest가 설치되어 있어야 합니다: `pip install pytest`
3. 로깅 설정이 올바르게 구성되어 있어야 합니다.
