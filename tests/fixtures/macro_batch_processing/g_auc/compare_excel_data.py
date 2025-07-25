from typing import Any
from utils.logs.sabangnet_logger import get_logger


logger = get_logger(__name__)


async def compare_sample_data_with_expected(
    self,
    sample_dict: list[dict[str, Any]],
    expect_dict: list[dict[str, Any]]
):
    """
    프로세스 거쳐 실제 나온 데이터와 예상 데이터 비교

    1. 순번 잘 들어가있는지
    2. 정렬 잘 됐는지 (순서 2, 3, 5, 6, 4)
    3. 금액 계산 잘 됐는지
    4. 제품명 N개 같이 개수 제거 됐는지
    5. 제품명 숫자만 있는 경우 하늘색으로 배경 있는지 -> dataframe 으로 들어오기 때문에 디자인 확인 불가
    6. 선/착불 신용인 경우 아무 것도 없고 착불인 경우 빨간색으로 금액 표시 -> dataframe 으로 들어오기 때문에 디자인 확인 불가
    7. 시트 분리 여부 (ok, cl, bb, iy)
    """
    
    # 필드 비교 대상
    comparison_fields = [
        "순번",
        "사이트",
        "수취인명",
        "금액",
        "주문번호",
        "제품명",
        "선/착불",
    ]

    # 비교 코드
    # 1. 데이터 길이 비교
    if len(sample_dict) != len(expect_dict):
        raise AssertionError(f"데이터 길이가 다릅니다. 실제: {len(sample_dict)}, 예상: {len(expect_dict)}")
    
    logger.info(f"데이터 길이 확인: {len(sample_dict)}개 행")
    
    # 2. 각 행별로 비교
    for row_idx, (sample_row, expect_row) in enumerate(zip(sample_dict, expect_dict)):
        
        # 3. 각 필드별로 비교
        for field in comparison_fields:
            sample_value = sample_row.get(field)
            expect_value = expect_row.get(field)
            
            # None 값 처리 (None과 빈 문자열은 같은 것으로 처리)
            if sample_value is None:
                sample_value = ""
            if expect_value is None:
                expect_value = ""
            
            # 문자열로 변환하여 비교 (타입 차이 방지)
            sample_str = str(sample_value).strip()
            expect_str = str(expect_value).strip()
            
            if sample_str != expect_str:
                raise AssertionError(f"행 {row_idx + 1}, 필드 '{field}' 불일치: {sample_str} != {expect_str}")
    
    # 4. 순번 연속성 확인
    for row_idx, sample_row in enumerate(sample_dict):
        expected_seq = str(row_idx + 1)
        actual_seq = str(sample_row.get("순번", "")).strip()
        
        if actual_seq != expected_seq:
            raise AssertionError(f"순번 오류 - 행 {row_idx + 1}: 실제 '{actual_seq}', 예상 '{expected_seq}'")
    
    logger.info("순번 연속성 확인 완료")
    
    # 5. 금액 필드 숫자 형태 확인
    for row_idx, sample_row in enumerate(sample_dict):
        amount = str(sample_row.get("금액", "")).strip()
        if amount and not amount.isdigit():
            raise AssertionError(f"금액 형태 오류 - 행 {row_idx + 1}: '{amount}' (숫자가 아님)")
    
    logger.info("금액 필드 형태 확인 완료")
    
    # 6. 제품명에서 'N개' 패턴 제거 확인
    for row_idx, sample_row in enumerate(sample_dict):
        product_name = str(sample_row.get("제품명", "")).strip()
        if " 1개" in product_name:
            raise AssertionError(f"제품명에 개수 정보 포함 - 행 {row_idx + 1}: '{product_name}'")
    
    logger.info("제품명 형태 확인 완료")
    
    # 7. 사이트별 분리 확인 (기본적인 사이트 정보 있는지만 확인)
    sites = set()
    for sample_row in sample_dict:
        site = str(sample_row.get("사이트", "")).strip()
        if site:
            sites.add(site)
    
    logger.info(f"사이트 정보 확인: {len(sites)}개 사이트 ({', '.join(list(sites)[:3])}...)")
    
    logger.info("모든 비교 통과")
    return True